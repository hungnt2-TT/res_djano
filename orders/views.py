from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect

from employee.models import Profile, EmployeeProfile
from marketplace.context_processors import get_cart_amount
from marketplace.models import Cart
from orders.forms import OrderForm
from orders.utils import generate_order_number
from wallet.models import PaymentMethod


# Create your views here.
@login_required(login_url='login')
def checkout(request):
    user_profile = Profile.objects.get(email=request.user.email)
    employee_profile = EmployeeProfile.objects.get(user=user_profile)

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
    form = OrderForm(initial=default_data)
    context = {
        'form': form
    }
    return render(request, 'checkout.html', context)


@login_required
@csrf_protect
def place_order(request):
    print(request.POST)
    cart_items = Cart.objects.filter(user=request.user).order_by('-created_at')
    cart_count = cart_items.count()
    if cart_count == 0:
        return redirect('home')
    subtotal = get_cart_amount(request.user)['subtotal']
    total_tax = 0.05 * subtotal
    total = subtotal + total_tax
    if request.method == 'POST':
        if 'order' in request.POST:
            return render(request, 'payment_paypal.html')
        form = OrderForm(request.POST)
        print(form)
        print(form.is_valid())
        print(form.errors)
        payment_method = convert_to_payment_method(request.POST.get('payment_method'))
        payment_id = get_object_or_404(PaymentMethod, method=payment_method)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.tax_data = subtotal
            order.total_tax = total_tax
            order.total = total
            order.payment = payment_id
            order.payment_method = request.POST.get('payment_method')
            order.save()
            order.order_number = generate_order_number(order.id)
            order.save()
            return redirect('place-order')
    return render(request, 'place_order.html')


def convert_to_payment_method(payment_method):
    if payment_method == 'PayPal':
        return 3
    elif payment_method == 'VnPay':
        return 1
    elif payment_method == 'Wallet':
        return 2
    elif payment_method == 'COD':
        return 4
    return 0


def transaction(request):
    return HttpResponse('Transaction')