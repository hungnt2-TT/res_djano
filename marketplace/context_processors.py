from collections import defaultdict

from .models import Cart
from menu.models import FoodItem
from django.db.models import Sum, F


def get_cart_counter(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        cart_count = cart.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    else:
        cart_count = 0
    return {'cart_count': cart_count}


def get_total_price_by_marketplace(request):
    if request.user.is_authenticated:
        subtotal = 0
        tax = 0
        total = 0
        cart = Cart.objects.filter(user=request.user, is_ordered=False)
        grouped_cart_items = defaultdict(list)
        for item in cart:
            grouped_cart_items[item.food_item.vendor].append(item)
        total_price_by_marketplace = []
        for vendor, items in grouped_cart_items.items():
            total_price = sum([item.total_price() for item in items])
            total_price_by_marketplace.append({'vendor': vendor, 'total_price': total_price})
    else:
        total_price_by_marketplace = []
    return {'total_price_by_marketplace': total_price_by_marketplace}


def get_cart_amount(request):
    subtotal = 0
    tax = 0
    grand_total = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_ordered=False)
        for item in cart:
            size_price = item.size.price if item.size else 0
            subtotal += size_price * item.quantity
        grand_total = subtotal + tax

    return dict(subtotal=subtotal, tax=tax, grand_total=grand_total)
