import json
import math
from lib2to3.fixes.fix_input import context

from celery import shared_task
from django.core.exceptions import ValidationError
from geopy.distance import geodesic

from django.contrib.auth.decorators import login_required
from django.contrib.gis.gdal.prototypes.errcheck import ptr_byref
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.conf import settings

from employee.models import Profile, EmployeeProfile
from marketplace.context_processors import get_cart_amount
from marketplace.distance import calculate_shipping_cost
from marketplace.models import Cart
from marketplace.views import get_distance_and_time
from menu.models import Coupon
from orders.forms import OrderForm
from orders.utils import generate_order_number
from vendor.models import Vendor
from wallet.models import PaymentMethod, Wallet
from collections import defaultdict
from django.db import transaction

from .models import Order, OrderedFood
from .tasks import validate_order_task, process_payment_task, notify_user_task, \
    track_delivery_status_task, complete_order_task, process_order


@login_required
@csrf_protect
# Create your views here.
def checkout(request):
    user_profile = Profile.objects.get(email=request.user.email)
    employee_profile = EmployeeProfile.objects.get(user=user_profile)
    cart_items = Cart.objects.filter(user=request.user, is_ordered=False).order_by('-created_at')
    profile_lat, profile_lng = employee_profile.latitude, employee_profile.longitude
    destination = f"{profile_lat},{profile_lng}"
    grouped_cart_items = defaultdict(lambda: {'items': [], 'total_price': 0})
    api_key = settings.GOOGLE_API_KEY_BY_IP

    subtotal = 0
    tax = 0
    total_shipping_cost = 0
    order_details = []

    for item in cart_items:
        vendor = item.food_item.vendor
        grouped_cart_items[vendor]['items'].append(item)
        grouped_cart_items[vendor]['total_price'] += item.get_total_price()

    grouped_cart_items = dict(grouped_cart_items)

    for item in cart_items:
        size_price = item.size.price if item.size else 0
        subtotal += size_price * item.quantity
    grand_total = subtotal + tax

    vendor_coordinates = []
    for vendor, data in grouped_cart_items.items():
        vendor_obj = Vendor.objects.get(vendor_name=vendor)
        vendor_coordinates.append({
            'vendor_name': vendor,
            'latitude': vendor_obj.latitude,
            'longitude': vendor_obj.longitude,
            'total_price': data['total_price']
        })
        for item in data['items']:
            order_details.append({
                "vendor": vendor_obj.id,
                "food_item": item.food_item.id,
                "size_id": item.size.id if item.size else None,
                "quantity": item.quantity,
                "price": item.get_total_price()
            })
    print('order_details = ', order_details)
    customer_coords = {'latitude': profile_lat, 'longitude': profile_lng}
    sorted_vendors = sort_vendors_by_distance(vendor_coordinates, customer_coords)
    print('sorted_vendors = ', sorted_vendors)
    total_duration = 0
    prev_coords = customer_coords
    for vendor_data in sorted_vendors:
        origin = f"{prev_coords['latitude']},{prev_coords['longitude']}"
        destination = f"{vendor_data['latitude']},{vendor_data['longitude']}"
        distance, duration = get_distance_and_time(api_key, origin, destination)

        total_duration += math.ceil(duration)

        shipping_cost = calculate_shipping_cost(distance)
        vendor_name = vendor_data['vendor_name']
        grouped_cart_items[vendor_name]['shipping_cost'] = shipping_cost
        grouped_cart_items[vendor_name]['time_to_deliver'] = math.ceil(duration)
        grouped_cart_items[vendor_name]['total_with_shipping'] = vendor_data['total_price'] + shipping_cost
        total_shipping_cost += shipping_cost

        prev_coords = vendor_data
    final_origin = f"{prev_coords['latitude']},{prev_coords['longitude']}"
    final_destination = f"{customer_coords['latitude']},{customer_coords['longitude']}"
    _, final_duration = get_distance_and_time(api_key, final_origin, final_destination)
    total_delivery_time = total_duration + final_duration
    print('total_delivery_time = ', total_delivery_time)
    final_grand_total = grand_total + int(total_shipping_cost)
    default_data = {
        'first_name': user_profile.first_name,
        'last_name': user_profile.last_name,
        'username': user_profile.username,
        'email': user_profile.email,
        'phone': user_profile.phone_number,
        'country': 'Viet Nam',
        'pin_code': '100000',
        'city': 'Ha noi',
        'address': employee_profile.address_line_2
    }

    if request.method == 'POST':
        print('total_shipping_cost = ', total_shipping_cost)

        print('request.POST = ', request.POST)
        new_total = request.POST.get('new_total')
        form = OrderForm(request.POST)
        print('form ==== ', form)
        print('form - ', form.errors)
        if form.is_valid():
            coupon_ids = request.POST.getlist('coupon_id')
            selected_coupon_id = next((id for id in coupon_ids if id), None)
            print('selected_coupon_id:', selected_coupon_id)
            context = {
                'profile': employee_profile,
                'form': form,
                'grouped_cart_items': grouped_cart_items.items(),
                'total_shipping_cost': int(total_shipping_cost),
                'final_grand_total': new_total,
                'coupon_id': selected_coupon_id,
                'coupon': request.POST.get('coupon'),
                'payment_method': request.POST.get('payment_method'),
                'total_delivery_time': math.ceil(total_delivery_time),
                'order_details': order_details
            }
            if request.POST.get('payment_method') == 'Cash':
                if user_profile.phone_number_verified:
                    return render(request, 'place_order.html', context=context)
                else:
                    return redirect('send_sms_view', user_profile.phone_number)
            return render(request, 'place_order.html', context=context)
    else:
        form = OrderForm(initial=default_data)

    current_time = timezone.now()
    coupons = Coupon.objects.filter(
        Q(coupon_expiry_date__gte=current_time) | Q(user=request.user),
    )

    context = {
        'profile': employee_profile,
        'form': form,
        'coupons': coupons,
        'grouped_cart_items': grouped_cart_items.items(),
        'total_shipping_cost': int(total_shipping_cost),
        'final_grand_total': final_grand_total,
    }
    return render(request, 'checkout.html', context)


@login_required
@csrf_protect
def place_order(request):
    if request.method == 'POST':
        print('request.POST = ', request.POST)
        data = {
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'phone': request.POST.get('phone'),
            'email': request.POST.get('email'),
            'country': request.POST.get('country'),
            'pin_code': request.POST.get('pin_code'),
            'city': request.POST.get('city'),
            'address': request.POST.get('address'),
            'state': request.POST.get('state'),
        }
        order_details = json.loads(request.POST.get('order_details'))
        form = OrderForm(data)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.user = request.user
                    order.subtotal = request.POST.get('subtotal', 0)
                    order.total_tax = request.POST.get('total_tax', 0)
                    order.total_shipping_cost = request.POST.get('total_shipping_cost', 0)
                    order.coupon = request.POST.get('coupon', '')
                    order.coupon_id = request.POST.get('coupon_id', None)
                    payment_method_str = request.POST.get('payment_method', '')
                    order.payment = PaymentMethod.objects.get(name=payment_method_str)
                    order.payment_method = convert_to_payment_method(payment_method_str)
                    order.total_delivery_time = request.POST.get('total_delivery_time', 0)
                    order.tax_data = request.POST.get('tax_data', {})
                    order.total = request.POST.get('final_grand_total', 0)
                    order.order_details = order_details
                    order.is_ordered = True
                    order.save()
                    order.order_number = generate_order_number(order.id)
                    order.save()
                    cart_items = Cart.objects.filter(user=request.user)
                    for item in cart_items:
                        ordered_food = OrderedFood()
                        ordered_food.order = order
                        ordered_food.payment = PaymentMethod.objects.get(name=payment_method_str)
                        ordered_food.user = request.user
                        ordered_food.fooditem = item.food_item
                        ordered_food.quantity = item.quantity
                        ordered_food.price = item.get_total_price()
                        ordered_food.size = item.size
                        ordered_food.save()
                    try:
                        process_order.delay(order.id)
                    except Exception as e:
                        raise ValidationError(f"Error processing order task: {str(e)}")

                    if order.message_error:
                        return JsonResponse({
                            'status': 'error',
                            'message': order.message_error
                        })
                    else:
                        return JsonResponse({
                            'status': 'success',
                            'message': 'Your order has been processed successfully.'
                        })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'An error occurred while processing your order: {str(e)}',
                })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'There was an error with your order form. Please try again.',
                'errors': form.errors
            })

    # Hiển thị trang đặt hàng nếu là GET request
    return render(request, 'place_order.html', {
        'form': OrderForm(),
        'cart_items': 1,
        'subtotal': 1,
        'total_tax': 1,
        'total': 1
    })


def convert_to_payment_method(payment_method):
    if payment_method == 'PayPal':
        return 3
    elif payment_method == 'VnPay':
        return 1
    elif payment_method == 'Wallet':
        return 2
    elif payment_method == 'Cash':
        return 4
    return 0


def transaction_order(request):
    return HttpResponse('Transaction')


def check_phone_verification(request):
    user_profile = Profile.objects.get(email=request.user.email)
    if user_profile.phone_number_verified:
        return JsonResponse({'status': 'success', 'message': 'Phone number is verified',
                             'phone_number_verified': user_profile.phone_number_verified})
    else:
        return JsonResponse({'status': 'failed', 'message': 'Phone number is not verified'})


def check_wallet_balance(request):
    user_profile = Profile.objects.get(email=request.user.email)
    wallet = Wallet.objects.get(user=user_profile)
    total = int(request.GET.get('total', 0))
    print('total = ', total)
    print('wallet.balance_point = ', wallet.balance_point)
    if wallet.balance_point >= 0 and wallet.balance_point >= total:
        return JsonResponse({'status': 'success', 'message': 'Wallet balance is enough',
                             'balance_point': wallet.balance_point})
    else:
        return JsonResponse({'status': 'failed', 'message': 'Wallet balance is not enough'})


def sort_vendors_by_distance(vendors, customer_coords):
    def distance_to_customer(vendor):
        vendor_coords = (vendor['latitude'], vendor['longitude'])
        customer_location = (customer_coords['latitude'], customer_coords['longitude'])
        return geodesic(vendor_coords, customer_location).kilometers

    sorted_vendors = sorted(vendors, key=distance_to_customer)
    return sorted_vendors


def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')

    context = {
        'orders': orders,
    }
    return render(request, 'my_order.html', context)


@login_required
def order_detail(request, order_number):
    try:
        order = get_object_or_404(Order, order_number=order_number)
        ordered_food = OrderedFood.objects.filter(order=order)
        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)
        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
            # 'tax_data': tax_data,
        }
        return render(request, 'order_detail.html', context)
    except:
        return redirect('customer')
