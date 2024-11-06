import math
from collections import defaultdict
from unicodedata import category

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from employee.models import EmployeeProfile
from marketplace.context_processors import get_cart_counter, get_total_price_by_marketplace, get_cart_amount
from marketplace.distance import calculate_distance, estimate_time, calculate_shipping_cost
from marketplace.models import Cart
from marketplace.templatetags.custom_filters import to_vnd_words
from menu.models import Category, FoodItem, Size
from vendor.models import Vendor


# Create your views here.
def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count
    }
    return render(request, 'listings.html', context)


def vendor_detail(request, vendor_slug):
    vendor = Vendor.objects.get(vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch('food_items', queryset=FoodItem.objects.filter(is_available=True)))
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user, is_ordered=False)
        context = {
            'vendor': vendor,
            'categories': categories,
            'cart_items': cart_items
        }
        return render(request, 'vendor_maketplace_detail.html', context)

    context = {
        'vendor': vendor,
        'categories': categories
    }
    return render(request, 'vendor_maketplace_detail.html', context)


@csrf_exempt
@login_required(login_url='login')
def add_to_cart(request, food_item_id):
    print('add_to_cart', request.POST)
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
            cart = Cart.objects.get(user=request.user, food_item=food_item, size=size, is_ordered=False)
            print('cart', cart.quantity)

            cart.quantity -= 1
            print('cart', cart)
            print('cart', cart.quantity)

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
    cart_items = Cart.objects.filter(user=request.user, is_ordered=False).order_by('-created_at')
    profile = EmployeeProfile.objects.get(user=request.user)
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
        # shipping_cost = calculate_shipping_cost(distance)
        shipping_cost = 15000
        data['shipping_cost'] = shipping_cost
        # data['time_to_deliver'] = math.ceil(duration)
        data['time_to_deliver'] = 30
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
            print('delete_cart_item', cart)
            # cart.delete()
            return JsonResponse({'cart_counter': get_cart_counter(request), 'status': 'success'})
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
