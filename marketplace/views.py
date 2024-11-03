from collections import defaultdict
from unicodedata import category

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
            quantity = int(request.POST.get('quantity', 1))

            food_item = get_object_or_404(FoodItem, id=food_item_id)
            print('food_item', food_item)
            size = get_object_or_404(Size, id=size_id)
            print('size', size)
            cart_item, created = Cart.objects.get_or_create(
                user=request.user,
                food_item=food_item,
                size=size,
                is_ordered=False,
                defaults={'quantity': quantity, 'note': request.POST.get('note', None)}
            )
            print('cart_item', cart_item)
            if not created:
                cart_item.quantity += quantity
                cart_item.note = request.POST.get('note', None)
                cart_item.save()
            return JsonResponse(
                {'quantity': cart_item.quantity, 'cart_counter': get_cart_counter(request),
                 'cart_amount': get_cart_amount(request), 'status': 'success'}
            )
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required(login_url='login')
def remove_from_cart(request, food_item_id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            food_item = FoodItem.objects.get(pk=food_item_id)
            cart = Cart.objects.get(user=request.user, food_item=food_item, is_ordered=False)
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


@login_required(login_url='login')
def cart(request):
    print('cart')
    cart_items = Cart.objects.filter(user=request.user, is_ordered=False).order_by('-created_at')
    profile = EmployeeProfile.objects.get(user=request.user)
    grouped_cart_items = defaultdict(lambda: {'items': [], 'total_price': 0})
    for item in cart_items:
        vendor = item.food_item.vendor
        grouped_cart_items[vendor]['items'].append(item)
        grouped_cart_items[vendor]['total_price'] += item.total_price()
    grouped_cart_items = dict(grouped_cart_items)
    for vendor, data in grouped_cart_items.items():
        print(f"Vendor: {vendor}, Total Price: {data['total_price']}, Items: {data['items']}")

    print('grouped_cart_items.items()0', grouped_cart_items.items())
    context = {
        'grouped_cart_items': grouped_cart_items.items(),
        'profile': profile
    }
    print('vcontext', cart_items)

    return render(request, 'cart.html', context)


@login_required(login_url='login')
def delete_cart_item(request, cart_id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            cart = Cart.objects.get(pk=cart_id, user=request.user)
            print('delete_cart_item', cart)
            cart.delete()
            return JsonResponse({'cart_counter': get_cart_counter(request), 'status': 'success'})
        except Exception as e:
            print(e)
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
