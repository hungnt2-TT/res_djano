import copy
import json

from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from customers.forms import CustomerForm, UserProfileForm, UserInfoForm
from employee import models as AccountModels
from django.contrib import messages

from django.shortcuts import render, redirect, get_object_or_404

from employee.models import Profile, EmployeeProfile
from marketplace.views import food_item
from menu.models import Size, FoodItem
from orders.models import Order
from django.utils import timezone
from datetime import datetime, timedelta
from .tasks import process_payment_bank_shipper_task
from vendor.models import Vendor


# Create your views here.
def cprofile(request):
    return render(request, 'customers/profile.html')


def customer_setting(request):
    profile = get_object_or_404(EmployeeProfile, user=request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserInfoForm(request.POST, instance=request.user)
        print(profile_form.errors)
        print('request.POST = ', request.POST)

        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'Profile updated')
            return redirect('cprofile')
        else:
            print(profile_form.errors)
            print(user_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserInfoForm(instance=request.user)

    context = {
        'profile_form': profile_form,
        'user_form': user_form,
        'profile': profile,
    }
    return render(request, 'customers/cprofile.html', context)


@login_required
def order_ship(request):
    user = request.user
    orders = Order.objects.filter(shipper=request.user).filter(Q(status='Shipper Accepted') | Q(status='Delivering'))
    print('Delivering', orders)
    date_range = request.GET.get('date_range', None)
    print('date_range', date_range)
    if date_range:
        try:
            if ' to ' in date_range:
                start_date_str, end_date_str = date_range.split(' to ')

                start_date = timezone.make_aware(datetime.strptime(start_date_str, '%Y-%m-%d'))
                end_date = timezone.make_aware(datetime.strptime(end_date_str, '%Y-%m-%d'))

                orders = orders.filter(created_at__range=[start_date, end_date])
                print('orders', orders)
                print('orders', orders.query)
            else:
                start_date_str = date_range
                start_date = timezone.make_aware(datetime.strptime(start_date_str, '%Y-%m-%d'))

                end_date = timezone.make_aware(datetime.strptime(start_date_str, '%Y-%m-%d') + timedelta(days=1))
                print('start_date', start_date)
                print('end_date', end_date)

                orders = orders.filter(created_at__range=[start_date, end_date])
                print('orders', orders)
                print('orders', orders.query)
        except ValueError:
            pass
    order_status = request.GET.get('order_status', None)
    if order_status:
        orders = orders.filter(status=order_status)
    order_statuses = Order.objects.values_list('status', flat=True).distinct()

    vendors_cache = {vendor.id: vendor for vendor in Vendor.objects.all()}
    sizes_cache = {size.id: size.size for size in Size.objects.all()}

    orders_with_details = []

    for order in orders:
        order_details_copy = copy.deepcopy(order.order_details)

        order_data = {
            'order_id': order.id,
            'order_number': order.order_number,
            'created_at': order.created_at,
            'subtotal': order.subtotal,
            'is_payment_completed': order.is_payment_completed,
            'shipper': order.shipper,
            'status': order.status,
            'user': order.user,
            'address': order.address,
            'phone_number': order.phone,
            'order_details': order_details_copy,
            'total_delivery_time': order.total_delivery_time,
            'total_shipping_cost': order.total_shipping_cost,
            'updated_at': order.updated_at,
            'total': order.total,
            'vendors': list(order.vendors.all()),
            'user_location': f'{order.lat}, {order.lng}',
            'shipper_location': order.shipper.employeeprofile.get_location(),
            'map': True if order.status == 'Delivering' else False,
            'proof_image': order.proof_image if order.proof_image else None,
        }
        print('order_data', order_data)
        for item in order_data['order_details']:
            food_item = FoodItem.objects.get(id=item['food_item'])
            item['food_name'] = food_item.food_name
            item['food_title'] = food_item.food_title
            item['size'] = sizes_cache.get(item['size_id'])
            item['vendor'] = vendors_cache.get(food_item.vendor_id)

        orders_with_details.append(order_data)

    context = {
        'order_statuses': order_statuses,
        'orders': orders_with_details,
    }
    return render(request, 'customers/shipping.html', context)


@csrf_exempt
def start_ship(request):
    if request.method == "POST":
        data = json.loads(request.body)
        order_id = data.get("order_id")
        try:
            order = Order.objects.get(id=order_id)
            order.status = "Delivering"
            order.save()
            return JsonResponse({"success": True, "message": "Order status updated successfully."})
        except Order.DoesNotExist:
            return JsonResponse({"success": False, "message": "Order not found."})
    return JsonResponse({"success": False, "message": "Invalid request method."})


@csrf_exempt
def complated_ship(request):
    if request.method == "POST":
        print('request.POST', request.POST)
        order_id = request.POST.get("order_id")
        proof_image = request.FILES.get("proof_image")
        print('proof_image', proof_image)
        if not proof_image:
            return JsonResponse({"success": False, "message": "Proof image is required."})
        try:
            order = Order.objects.get(id=order_id, status="Delivering")
            if order.shipper != request.user:
                return JsonResponse({"success": False, "message": "Permission denied."})

            proof_path = default_storage.save(f"proof_images/{order_id}/{proof_image.name}", proof_image)
            print('proof_path', proof_path)
            order.proof_image = proof_path
            order.status = "Completed"
            order.save()
            for item in order.order_details:
                food_item_id = item['food_item']
                quantity = item['quantity']
                food_item = FoodItem.objects.get(id=food_item_id)
                food_item.quantity_order += quantity
                food_item.save()

            process_payment_bank_shipper_task.delay(order.id)

            return JsonResponse({"success": True})
        except Order.DoesNotExist:
            return JsonResponse({"success": False, "message": "Order not found."})
