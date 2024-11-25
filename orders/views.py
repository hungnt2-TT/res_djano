import json
import math
from lib2to3.fixes.fix_input import context
from django.views.decorators.http import require_POST
from django.http import JsonResponse
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

from employee.decorators import restrict_employee_types
from employee.models import Profile, EmployeeProfile
from marketplace.context_processors import get_cart_amount
from marketplace.distance import calculate_shipping_cost
from marketplace.models import Cart
from marketplace.views import get_distance_and_time
from menu.models import Coupon
from orders.forms import OrderForm
from orders.utils import generate_order_number
from vendor.models import Vendor
from wallet.models import PaymentMethod, Wallet, Transaction, SubTransaction
from collections import defaultdict
from django.db import transaction

from .models import Order, OrderedFood
from .tasks import validate_order_task, process_payment_task, notify_user_task, \
    track_delivery_status_task, complete_order_task, process_order


@login_required
@csrf_protect
@restrict_employee_types
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
        lat, lng = vendor_obj.latitude, vendor_obj.longitude
        origin = f"{lat},{lng}"
        distance, duration = get_distance_and_time(api_key, origin, destination)
        shipping_cost = calculate_shipping_cost(distance)
        data['shipping_cost'] = shipping_cost
        data['time_to_deliver'] = math.ceil(duration) if duration else 30
        vendor_total_price = data['total_price'] + shipping_cost
        data['total_with_shipping'] = vendor_total_price
        total_shipping_cost += shipping_cost


        for item in data['items']:
            order_details.append({
                "vendor": vendor_obj.id,
                "food_item": item.food_item.id,
                "size_id": item.size.id if item.size else None,
                "quantity": item.quantity,
                "price": item.get_total_price()
            })
    # print('order_details = ', order_details)
    # customer_coords = {'latitude': profile_lat, 'longitude': profile_lng}
    # sorted_vendors = sort_vendors_by_distance(vendor_coordinates, customer_coords)
    # print('sorted_vendors = ', sorted_vendors)
    # total_duration = 0
    # prev_coords = customer_coords
    # for vendor_data in sorted_vendors:
    #     origin = f"{prev_coords['latitude']},{prev_coords['longitude']}"
    #     destination = f"{vendor_data['latitude']},{vendor_data['longitude']}"
    #     distance, duration = get_distance_and_time(api_key, origin, destination)
    #
    #     total_duration += math.ceil(duration)
    #
    #     shipping_cost = calculate_shipping_cost(distance)
    #     vendor_name = vendor_data['vendor_name']
    #     grouped_cart_items[vendor_name]['shipping_cost'] = shipping_cost
    #     grouped_cart_items[vendor_name]['time_to_deliver'] = math.ceil(duration)
    #     grouped_cart_items[vendor_name]['total_with_shipping'] = vendor_data['total_price'] + shipping_cost
    #     total_shipping_cost += shipping_cost
    #
    #     prev_coords = vendor_data
    # final_origin = f"{prev_coords['latitude']},{prev_coords['longitude']}"
    # final_destination = f"{customer_coords['latitude']},{customer_coords['longitude']}"
    # _, final_duration = get_distance_and_time(api_key, final_origin, final_destination)
    time_to_deliver = math.ceil(total_shipping_cost)
    final_grand_total = grand_total + int(total_shipping_cost)
    default_data = {
        'first_name': user_profile.first_name,
        'last_name': user_profile.last_name,
        'username': user_profile.username,
        'email': user_profile.email,
        'phone': user_profile.phone_number,
        'country': 'Viet Nam',
        'pin_code': '',
        'city': '',
        'address': ''
    }

    if request.method == 'POST':

        new_total = request.POST.get('new_total')
        form = OrderForm(request.POST)
        if form.is_valid():
            coupon_ids = request.POST.getlist('coupon_id')
            selected_coupon_id = next((id for id in coupon_ids if id), None)
            total_delivery_time = sum(data['time_to_deliver'] for data in grouped_cart_items.values())
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
                'order_details': order_details,
                'lat': request.POST.get('lat'),
                'lng': request.POST.get('lng'),
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
    global_coupons = Coupon.objects.filter(
        user__isnull=True,
        vendor__isnull=True,
        coupon_expiry_date__gte=current_time
    )
    user_coupons = Coupon.objects.filter(
        user=request.user,
        coupon_expiry_date__gte=current_time,
        redeemed=False
    )
    vendor_coupons = Coupon.objects.filter(
        vendor__in=grouped_cart_items.keys(),
        coupon_expiry_date__gte=current_time
    )
    coupons = global_coupons | user_coupons | vendor_coupons
    coupons = coupons.distinct()

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
@restrict_employee_types
def place_order(request):
    if request.method == 'POST':
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
        vendor_ids = list({item['vendor'] for item   in order_details if 'vendor' in item})
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
                    order.coupon_id = request.POST.get('coupon_id', 0)
                    payment_method_str = request.POST.get('payment_method', '')
                    order.payment = PaymentMethod.objects.get(name=payment_method_str)
                    order.payment_method = convert_to_payment_method(payment_method_str)
                    order.total_delivery_time = request.POST.get('total_delivery_time', 0)
                    order.tax_data = request.POST.get('tax_data', {})
                    order.total = request.POST.get('final_grand_total', 0)
                    order.order_details = order_details
                    order.is_ordered = True
                    order.is_payment_completed = False
                    order.lat = float(request.POST.get('lat', 0))
                    order.lng = float(request.POST.get('lng', 0))
                    order.save()
                    order.order_number = generate_order_number(order.id)
                    order.vendors.set(Vendor.objects.filter(id__in=vendor_ids))
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

                        item.is_ordered = True
                        item.save()
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
                        print('order = ', order.id)
                        return JsonResponse({
                            'status': 'success',
                            'redirect_url': reverse('paypal_payment', kwargs={'order_id': order.id}),
                            'success_url': reverse('payment_success'),
                            'failed_url': reverse('payment_failed'),
                            'vn_pay_url': reverse('payment', kwargs={'order_id': order.id}),
                            'message': 'Your order has been processed successfully.',
                            'order_detail': reverse('order_detail', kwargs={'order_number': order.order_number}),
                            'order': {
                                'id': order.id,
                                'order_number': order.order_number,
                                'total': order.total,
                                'payment_method': order.payment_method,
                                'status': order.status,
                                'created_at': order.created_at,
                            }
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
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-updated_at')
    context = {
        'orders': orders,
    }
    print('orders = ', orders)
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


@require_POST
def confirm_paypal_payment(request):
    try:
        data = json.loads(request.body)
        order_number = data.get('orderNumber')
        payment_id = data.get('paymentID')

        order = get_object_or_404(Order, order_number=order_number)
        order.status = 'Waiting for Confirmation'
        order.is_payment_completed = True
        order.save()
        admin = Profile.objects.get(is_superuser=True)

        transaction = Transaction.objects.create(
            transaction_type=Transaction.TRANSACTION_TYPE_DEPOSIT,
            wallet=admin.wallet,
            status=Transaction.STATUS_COMPLETED,
            user_id_from=admin,
            user_id_to=order.user,
            description=f'Payment for order {order.order_number} and Paypal id {payment_id}',
            create_at=timezone.now(),
            update_at=timezone.now()
        )
        SubTransaction.objects.create(
            transaction_id=transaction,
            wallet_id_from=admin.wallet,
            wallet_id_to=order.user.wallet,
            amount_cash=order.total,
            amount_point=0,
            description='Payment PayPal',
            status=Transaction.STATUS_COMPLETED,
            create_at=timezone.now(),
            update_at=timezone.now()
        )

        return JsonResponse({'status': 'success'})
    except:
        return JsonResponse({'status': 'error'})


def payment_success(request):
    return render(request, "payment/payment_success.html")


def payment_failed(request):
    return render(request, 'payment/payment_failed.html')
