import json
import math
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from http.client import responses
from unicodedata import category

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from employee.models import EmployeeProfile, Profile
from marketplace.context_processors import get_cart_counter, get_total_price_by_marketplace, get_cart_amount
from marketplace.distance import calculate_distance, estimate_time, calculate_shipping_cost
from marketplace.forms import ReservationForm
from marketplace.models import Cart
from marketplace.templatetags.custom_filters import to_vnd_words
from menu.models import Category, FoodItem, Size, Coupon
from orders.forms import OrderForm
from orders.models import Order
from vendor.models import Vendor
from wallet.models import Transaction, Wallet, SubTransaction
from wallet.tasks import convert_currency, format_currency_conversion


# Create your views here.
def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count
    }
    return render(request, 'listings.html', context)


def food_item_recomment(request):
    current_hour = timezone.now().hour + 7

    if 6 <= current_hour < 12:
        time_range = 'morning'
    elif 12 <= current_hour < 18:
        time_range = 'afternoon'
    elif 18 <= current_hour < 24:
        time_range = 'evening'
    else:
        time_range = 'evening'

    food_items = FoodItem.objects.filter(Q(time_range=time_range) | Q(time_range='all_day'))

    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
        'food_items': food_items,
        'food_item_count': food_items.count()
    }
    return render(request, 'list_fooditem.html', context)


def food_item(request):
    food_items = FoodItem.objects.all()
    print('food_items', food_items)
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    context = {
        'vendors': vendors,
        'food_items': food_items,
        'food_item_count': food_items.count()
    }
    return render(request, 'list_fooditem.html', context)


@csrf_exempt
def vendor_detail(request, vendor_slug):
    vendor = Vendor.objects.get(vendor_slug=vendor_slug)
    vendor_id = vendor.id
    vendor_slug = vendor.vendor_slug
    user = Profile.objects.get(email=request.user.email)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch('food_items', queryset=FoodItem.objects.filter(is_available=True)))
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user, is_ordered=False)

        user_data = {
            'first_name': user.first_name if user.first_name else '',
            'last_name': user.last_name if user.last_name else '',
            'email': user.email,
            'phone_number': user.phone_number,
            'name': user.username,
            'user': user,
            'vendor': vendor
        }
        print('vendor_id', vendor_id)
        form = ReservationForm(initial=user_data)
        context = {
            'vendor': vendor,
            'vendor_slug': vendor_slug,
            'categories': categories,
            'cart_items': cart_items,
            'form': form,
            'vendor_id': vendor.id
        }
        return render(request, 'vendor_maketplace_detail.html', context)

    context = {
        'vendor': vendor,
        'vendor_slug': vendor_slug,
        'categories': categories,
        'vendor_id': vendor.id
    }
    return render(request, 'vendor_maketplace_detail.html', context)


@csrf_exempt
@login_required(login_url='login')
def add_to_cart(request, food_item_id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            size_id = request.POST.get('firstSizeId')
            if size_id is not None:
                size_id = int(size_id)
                if size_id == 0:
                    print('size_id', size_id)
                    size_id = 1
            print('size_id', size_id)
            quantity = int(request.POST.get('quantity', 1))
            food_item = get_object_or_404(FoodItem, id=food_item_id)
            size = get_object_or_404(Size, id=size_id)
            cart_item, created = Cart.objects.get_or_create(
                user=request.user,
                food_item=food_item,
                vendor=food_item.vendor,
                size=size,
                is_ordered=False,
                defaults={'quantity': quantity, 'note': request.POST.get('note', None)}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.note = request.POST.get('note', None)
                cart_item.save()
            return JsonResponse(
                {'quantity': cart_item.quantity, 'cart_counter': get_cart_counter(request),
                 'cart_amount': get_cart_amount(request), 'status': 'success', 'message': 'Added to cart'}
            )
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@csrf_exempt
@login_required(login_url='login')
def remove_from_cart(request, food_item_id):
    print('remove_from_cart', request.POST)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            food_item = FoodItem.objects.get(pk=food_item_id)
            size_id = request.POST.get('firstSizeId')
            cart_user = request.user
            size = get_object_or_404(Size, id=size_id)
            cart = Cart.objects.get(user=request.user, food_item=food_item, vendor=food_item.vendor, size=size,
                                    is_ordered=False)
            cart.quantity -= 1
            if cart.quantity == 0:
                cart.delete()
            else:
                cart.save()
            return JsonResponse({'quantity': cart.quantity, 'cart_counter': get_cart_counter(request),
                                 'cart_amount': get_cart_amount(request), 'status': 'success'})
        except Exception as e:
            print(e)
    return render(request, 'vendor_maketplace_detail.html')


def get_distance_and_time(api_key, origin, destination, mode="driving"):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": origin,
        "destinations": destination,
        "mode": mode,
        "key": api_key
    }
    response = requests.get(url, params=params)
    print('response', response)
    data = response.json()
    print('data = ', data)

    if data["status"] == "OK":
        element = data["rows"][0]["elements"][0]
        if element["status"] == "OK":
            distance = element["distance"]["value"] / 1000
            duration = element["duration"]["value"] / 60
            return distance, duration
        else:
            print("Error with element:", element["status"])
    else:
        print("Error with API request:", data["status"])

    return None, None


@csrf_exempt
@login_required(login_url='login')
def cart(request):
    user_profile = Profile.objects.get(email=request.user.email)
    profile = EmployeeProfile.objects.get(user=request.user)
    cart_items = Cart.objects.filter(user=request.user, is_ordered=False).order_by('-created_at')
    profile_lat, profile_lng = profile.latitude, profile.longitude
    destination = f"{profile_lat},{profile_lng}"
    grouped_cart_items = defaultdict(lambda: {'items': [], 'total_price': 0})
    api_key = settings.GOOGLE_API_KEY_BY_IP

    subtotal = 0
    tax = 0
    total_shipping_cost = 0

    for item in cart_items:
        vendor = item.food_item.vendor
        grouped_cart_items[vendor]['items'].append(item)
        grouped_cart_items[vendor]['total_price'] += item.get_total_price()

    grouped_cart_items = dict(grouped_cart_items)

    for item in cart_items:
        size_price = item.size.price if item.size else 0
        subtotal += size_price * item.quantity
    grand_total = subtotal + tax

    for vendor, data in grouped_cart_items.items():
        vendor_obj = Vendor.objects.get(vendor_name=vendor)
        lat, lng = vendor_obj.latitude, vendor_obj.longitude
        origin = f"{lat},{lng}"
        distance, duration = get_distance_and_time(api_key, origin, destination)
        shipping_cost = calculate_shipping_cost(distance)
        print('shipping_cost', shipping_cost)
        # shipping_cost = 15000
        data['shipping_cost'] = shipping_cost
        data['time_to_deliver'] = math.ceil(duration) if duration else 30
        # data['time_to_deliver'] = 30
        vendor_total_price = data['total_price'] + shipping_cost
        data['total_with_shipping'] = vendor_total_price
        total_shipping_cost += shipping_cost

    final_grand_total = grand_total + total_shipping_cost
    context = {
        'grouped_cart_items': grouped_cart_items.items(),
        'profile': profile,
        'total_shipping_cost': total_shipping_cost,
        'final_grand_total': final_grand_total,
    }

    return render(request, 'cart.html', context)


@csrf_exempt
@login_required(login_url='login')
def delete_cart_item(request, cart_id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            size = request.POST.get('firstSizeId')
            cart = Cart.objects.get(pk=cart_id, user=request.user, size=size)
            cart.delete()
            return JsonResponse({'cart_counter': get_cart_counter(request),
                                 'cart_amount': get_cart_amount(request),
                                 'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return render(request, 'cart.html')


def convert_to_words(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        amount = request.POST.get('amount', None)
        if amount:
            words = to_vnd_words(amount)
            return JsonResponse({'words': words})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def search(request):
    address = request.GET.get('address')
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    keyword = request.GET.get('keyword')
    radius = request.GET.get('radius')
    sort_by = request.GET.get('sort_by')
    print('address', request.GET)
    print('sort_by', sort_by)
    if not keyword:
        return redirect('marketplace')

    food_item_query = FoodItem.objects.filter(
        food_name__icontains=keyword, is_available=True
    ).values_list('vendor', flat=True)

    vendors = Vendor.objects.filter(
        Q(vendor_name__icontains=keyword) | Q(vendor_food_items__in=food_item_query)
    ).distinct()

    print('vendors', vendors)
    if lat and lng and radius:
        try:
            pnt = GEOSGeometry(f'POINT({lng} {lat})', srid=4326)
            vendors = vendors.filter(
                location__distance_lte=(pnt, D(km=radius))
            ).annotate(distance=Distance('location', pnt)).order_by('distance')
            for vendor in vendors:
                vendor.kms = round(vendor.distance.km, 2)
        except Exception as e:
            print(e)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if sort_by == 'alphabetical':
            vendors = vendors.order_by('vendor_name')
        vendor_list = []
        for vendor in vendors:
            profile_picture_url = vendor.user_profile.profile_picture.url if vendor.user_profile.profile_picture else 'default_image_url'
            vendor_info = {
                'vendor_name': vendor.vendor_name,
                'vendor_slug': vendor.vendor_slug,
                'profile_picture': profile_picture_url,
                'address_line_1': vendor.address_line_1,
                'kms': vendor.kms if hasattr(vendor, 'kms') else None
            }
            vendor_list.append(vendor_info)

        return JsonResponse({'vendors': vendor_list})

    context = {
        'vendors': vendors,
        'vendor_count': vendors.count(),
        'address': address,
    }

    return render(request, 'listings.html', context)


def food_item_detail(request, id):
    food_item = get_object_or_404(FoodItem, id=id)
    sizes = Size.objects.filter(food_item=food_item)
    contex = {
        'food_item': food_item,
        'sizes': sizes
    }
    return render(request, 'food_item_detail.html', contex)


@csrf_exempt
def apply_coupon_discount(request):
    if request.method == 'POST':
        try:
            coupon_id = request.POST.get('coupon_id')
            subtotal = int(request.POST.get('subtotal'))
            tax = int(request.POST.get('tax'))
            shipping = int(request.POST.get('shipping'))
            total = int(request.POST.get('total'))

            coupon = get_object_or_404(Coupon, id=coupon_id)

            if coupon.is_valid():
                discount = coupon.apply_discount(total, shipping)

                new_total = total - discount['discount']
                if coupon.type_of_discount == Coupon.REFUND_COIN:
                    response_data = {
                        'discount': discount,
                        'new_total': new_total,
                        'refund_coin': discount['refund_coin'],
                        'message': 'Coupon applied successfully. Refund coin will be credited to your account.',
                        'status': 'success'
                    }
                else:
                    response_data = {
                        'discount': discount,
                        'new_total': new_total,
                        'refund_coin': 0,
                        'message': 'Coupon applied successfully.',
                        'status': 'success'
                    }
            else:
                response_data = {
                    'discount': 0,
                    'new_total': total,
                    'refund_coin': 0,
                    'message': 'Coupon is not valid.',
                    'status': 'error'
                }

            return JsonResponse(response_data)
        except (InvalidOperation, ValueError) as e:
            return JsonResponse({'error': 'Invalid input data.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


@csrf_exempt
def reservation_booking(request):
    print('reservation_booking', request.POST)
    vendor_id = request.POST.get('vendor_id')
    print('vendor_id', vendor_id)
    vendor = Vendor.objects.get(id=vendor_id)
    user = Profile.objects.get(email=request.user.email)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch('food_items', queryset=FoodItem.objects.filter(is_available=True)))
    cart_items = Cart.objects.filter(user=request.user, is_ordered=False)
    print('categories', categories)
    print('cart_items', request.POST.get('phone_number'))
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['vendor'] = vendor.id
        post_data['user'] = user.id
        form = ReservationForm(post_data)
        print('form', form.errors)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reservation has been booked successfully')
            return redirect('marketplace')
        else:
            context = {
                'form': form,
                'vendor': vendor,
                'vendor_id': vendor.id,
                'categories': categories,
                'cart_items': cart_items
            }
            messages.error(request, 'Reservation booking failed')
            return render(request, 'vendor_maketplace_detail.html', context)
    else:
        form = ReservationForm()
    context = {
        'form': form,
        'vendor': vendor,
        'vendor_id': vendor.id,
        'categories': categories,
        'cart_items': cart_items
    }
    return render(request, 'vendor_maketplace_detail.html', context)


def paypal_payment(request, order_id):
    # success_url = reverse('success')
    # error_url = reverse('error')
    order = get_object_or_404(Order, id=order_id)
    converted_total = convert_currency(order.total, from_currency="VND", to_currency="USD")
    print('converted_total', converted_total)
    if converted_total is None:
        return render(request, 'payment_error.html', {'message': 'Could not convert currency.'})
    formatted_total = format_currency_conversion(order.total, from_currency="VND", to_currency="USD")
    print('formatted_total', formatted_total)
    context = {
        'order': order,
        'converted_total': converted_total,
        'formatted_total': formatted_total,
        # 'success_url': success_url,
        # 'error_url': error_url
    }
    return render(request, 'payment_paypal.html', context)

# @require_POST
# def confirm_paypal_payment(request):
#     data = json.loads(request.body)
#     order_number = data.get('orderNumber')
#     payment_id = data.get('paymentID')
#
#     order = get_object_or_404(Order, order_number=order_number)
#     order.payment_id = payment_id
#     order.status = 'Waiting for Confirmation'
#     order.is_payment_completed = True
#     order.save()
#     admin = Profile.objects.get(is_superuser=True)
#
#     transaction = Transaction.objects.create(
#         transaction_type=Transaction.TRANSACTION_TYPE_DEPOSIT,
#         wallet=admin.wallet,
#         status=Transaction.STATUS_COMPLETED,
#         user_id_from=admin,
#         user_id_to=order.user,
#         description='Payment PayPal',
#         create_at=timezone.now(),
#         update_at=timezone.now()
#     )
#     SubTransaction.objects.create(
#         transaction_id=transaction,
#         wallet_id_from=admin.wallet,
#         wallet_id_to=order.user.wallet,
#         amount_cash=order.total,
#         amount_point=0,
#         description='Payment PayPal',
#         status=Transaction.STATUS_COMPLETED,
#         create_at=timezone.now(),
#         update_at=timezone.now()
#     )
#
#     return JsonResponse({'status': 'success'})
