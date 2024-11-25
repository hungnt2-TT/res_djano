import copy
from decimal import Decimal
from traceback import print_tb
from datetime import datetime, timedelta
from django.utils import timezone
from geopy.geocoders import Nominatim

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms import inlineformset_factory
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import F
from geopy import Point

from employee import consts
from employee.consts import PAGE
from employee.forms import RegisterForm, ShipperRegistrationForm
from employee.models import EmployeeProfile, Profile
from employee.paginations import paginate_data
from menu.forms import CategoryForm, FoodItemForm, SizeForm
from menu.models import Category, FoodItem, Size
from orders.models import Order, OrderedFood
from vendor.forms import VendorForm, VendorUpdateForm, VendorUpdateMapForm, OpeningHourForm
from django.conf import settings
from vendor.models import Vendor, OpeningHour, Favorite
from wallet.models import Wallet
from django.db import transaction
from django.http import HttpResponseServerError

import os
import json


def upload_file(file_name):
    if file_name:
        file_path = os.path.join(settings.MEDIA_ROOT, file_name.name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb+') as destination:
            for chunk in file_name.chunks():
                destination.write(chunk)
        file_url = settings.MEDIA_URL + file_name.name
        return file_url

    return None


def render_file_img(request, file_name):
    if file_name:
        file_url = settings.MEDIA_URL + file_name.name
        return file_url
    return None


def get_type_vendor():
    vendor_type = Vendor.VENDOR_TYPE_CHOICES
    return vendor_type


def handle_confirm(request, form, vendor_form, upload_file_url):
    if form.is_valid() and vendor_form.is_valid():
        print('request.POST', request.POST)
        request.session['form_data'] = request.POST.copy()
        request.session['form_data'].update(upload_file_url=upload_file_url)
        vendor_type = get_type_vendor()
        return render(request, 'vendor/register_vendor_package.html', {
            "form": form,
            "vendor_form": vendor_form,
            "vendor_type": vendor_type,
        })
    return render(request, 'vendor/register_vendor.html', {
        "form": form,
        "vendor_form": vendor_form,
    })


def handle_back(request, form, vendor_form):
    return render(request, 'vendor/register_vendor.html', {
        "form": form,
        "vendor_form": vendor_form,
    })


def handle_next_payment(request, form, vendor_form):
    form_data = request.session.get('form_data', {})
    vendor_type_value = request.POST.get('vendor_type', '')
    if vendor_type_value.isdigit():
        form_data.update({'vendor_type': int(vendor_type_value)})
        request.session['form_data'] = form_data  # Update the session data
        return render(request, 'vendor/register_vendor_payment.html', {
            "form": form,
            "vendor_form": vendor_form,
            "form_data": form_data,
        })
    return render(request, 'vendor/register_vendor.html', {
        "form": form,
        "vendor_form": vendor_form,
    })


def handle_send(request):
    try:
        form_data = request.session.get('form_data', {})
        if form_data:
            with transaction.atomic():
                user = Profile.objects.create_user(
                    username=form_data.get('username', ''),
                    email=form_data.get('email', ''),
                    password=form_data.get('password1', ''),
                    first_name=form_data.get('first_name', ''),
                    last_name=form_data.get('last_name', ''),
                )
                user.is_active = True
                user.employee_type = 1
                user.save()

                employee = EmployeeProfile.objects.filter(user=user).first()
                employee.success_privacy_policy = True
                employee.save()
                Vendor.objects.create(
                    user=user,
                    user_profile=employee,
                    vendor_name=form_data.get('vendor_name', ''),
                    fax_number=form_data.get('fax_number', ''),
                    vendor_type=form_data.get('vendor_type', ''),
                    vendor_license=form_data.get('upload_file_url', ''),
                    is_approved=False,
                    address_line_1=form_data.get('address_line_1', ''),
                    state=form_data.get('state', ''),
                    city=form_data.get('city', ''),
                    longitude=form_data.get('foodbakery_post_loc_longitude_restaurant', ''),
                    latitude=form_data.get('foodbakery_post_loc_latitude_restaurant', ''),
                )
            messages.info(request, 'Please check your email to confirm your account')
            return render(request, 'vendor/register_vendor_send.html', {
                "form_data": form_data,
            })
        return redirect('vendor:register_vendor')

    except Exception as e:
        print('error', e)
        messages.error(request, 'Vendor not added')
        return HttpResponseServerError('Internal Server Error')


def register_vendor(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in')
        return redirect('home')
    print('request', request)
    upload_file_url = upload_file(request.FILES.get('vendor_license'))
    form = RegisterForm(request.POST or None)
    vendor_form = VendorForm(request.POST or None)
    if request.method == 'POST':
        next_action = request.POST.get('next', '')
        if next_action == 'confirm':
            return handle_confirm(request, form, vendor_form, upload_file_url)
        elif next_action == 'back':
            return handle_back(request, form, vendor_form)
        elif next_action == 'next_payment':
            return handle_next_payment(request, form, vendor_form, )
        elif next_action == 'send':
            return handle_send(request)

    return render(request, 'vendor/register_vendor.html', {
        "form": form,
        "vendor_form": vendor_form,
        "upload_file_url": upload_file_url,
    })


def register_shipper(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in')
        return redirect('home')
    if request.method == 'POST':
        form = ShipperRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            shipper = form.save(commit=False)
            shipper.is_active = False
            shipper.employee_type = 5
            form.save()
            messages.info(request, 'Please check your email to confirm your account')
            return render(request, 'vendor/register_shipper_success.html', {
                "form": form,
            })
    else:
        form = ShipperRegistrationForm()
    return render(request, 'vendor/register_shipper.html', {'form': form})
    # upload_file_url = upload_file(request.FILES.get('vendor_license'))
    # form = RegisterForm(request.POST or None)
    # profile_shipper_form = ShipperProfileForm(request.POST or None)
    # if request.method == 'POST':
    #     next_action = request.POST.get('next', '')
    #     if next_action == 'confirm':
    #         pass
    #
    #
    # return render(request, 'vendor/register_shipper.html', {
    #     "form": form,
    #     "upload_file_url": upload_file_url,
    # })



def vendor_map(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    vendor_form = VendorUpdateMapForm(instance=vendor)

    if request.method == 'POST':
        print('request.POST', request.POST)
        vendor_form = VendorUpdateMapForm(request.POST, instance=vendor)
        if vendor_form.is_valid():
            vendor.pin_code = request.POST.get('pin_code')
            vendor.address_line_1 = request.POST.get('address_line_1')
            vendor.latitude = request.POST.get('latitude')
            vendor.longitude = request.POST.get('longitude')
            vendor.save()
            messages.success(request, 'Vendor updated successfully')
            return redirect('vendor_map')

        else:
            messages.error(request, 'Invalid address')
            return redirect('vendor_map')

    ctx = {
        'vendor_form': vendor_form,
        'initSearchBox': 'initSearchBox'
    }
    return render(request, 'vendor/vendor_map_update.html', ctx)


def get_menu(request, form=None, type_data=None, *args, **kwargs):
    vendor = Vendor.objects.get(user=request.user)
    list_category = Category.objects.filter(vendor=vendor).order_by('created_at')

    page = request.GET.get('page', PAGE)
    page_size = request.GET.get('page_size', consts.PAGE_SIZE)
    if type_data == 'food':
        food_items = FoodItem.objects.filter(category__id=F('category_id'),
                                             vendor__id=F('category__vendor__id')).select_related('category').order_by(
            'created_at')
        sizes = Size.objects.filter(food_item__id=F('food_item_id')).select_related('food_item')
        size_edit = Size.objects.all()
        category_ids = food_items.values_list('category_id', flat=True).distinct()
        categories = Category.objects.filter(vendor=vendor, id__in=category_ids)
        print('categories', categories)
        menus_pagination = paginate_data(categories, page_size, page)

        context = {
            'categories': list_category,
            'menus_pagination': menus_pagination,
            'food_form': form,
            'foods': food_items,
            'category_food': categories,
            'sizes': sizes,
        }
        return context
    else:
        menus_pagination = paginate_data(list_category, page_size, page)
        context = {
            'categories': list_category,
            'menus_pagination': menus_pagination,
            'category_form': form,
        }
    return context


@csrf_exempt
@login_required
def menu_builder(request):
    if request.method == 'POST':
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category = category_form.save(commit=False)
            category.vendor = Vendor.objects.get(user=request.user)
            category.save()
            category.slug = slugify(category.category_name) + '-' + str(category.id)
            category.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'message': 'Category added successfully!', 'alert': 'success'}, status=200)
            messages.success(request, 'Category added successfully')
            return redirect('menu_builder')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse(
                    {'errors': category_form.errors, 'message': 'Category name already exists!', 'alert': 'danger'},
                    status=400)
            messages.error(request, 'Category not added')
            return redirect('menu_builder')
    else:
        category_form = CategoryForm()
        context = get_menu(request, category_form)
        return render(request, 'vendor/vendor_menu_builder.html', context)


@csrf_exempt
@login_required
def food_menu(request):
    SizeFormSet = inlineformset_factory(FoodItem, Size, form=SizeForm, extra=3)
    if request.method == 'POST':
        print('request.POST', request.POST)
        food_form = FoodItemForm(request.POST or None, request.FILES)
        size_formset = SizeFormSet(request.POST, instance=food_form.instance)
        print('food_form', food_form.errors)
        print('size_formset', size_formset.errors)
        if food_form.is_valid() and size_formset.is_valid():
            food = food_form.save(commit=False)
            food.category = Category.objects.get(pk=request.POST.get('category'))
            food.vendor = Vendor.objects.get(user=request.user)
            food.slug = slugify(food.food_name) + '-' + str(food.id)
            food.save()
            size_formset.instance = food
            size_formset.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'message': 'Food added successfully!', 'alert': 'success'}, status=200)
            messages.success(request, 'Food added successfully')
            return redirect('food_menu')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse(
                    {'errors': food_form.errors, 'message': 'Food not added', 'alert': 'danger'},
                    status=400)
            messages.error(request, 'Food not added')
            return redirect('food_menu')
    else:
        food_form = FoodItemForm()
        size_formset = SizeFormSet(instance=FoodItem())
        print('size_formset', size_formset)
        context = get_menu(request, food_form, 'food')
        context['ckeditor_config'] = settings.CKEDITOR_5_CONFIGS['extends']
        context['size_formset'] = size_formset
        return render(request, 'vendor/vendor_food.html', context)


@csrf_exempt
@login_required
@require_http_methods(["PATCH"])
def menu_edit_detail(request, pk):
    try:
        print('request.body', request.body)
        category = Category.objects.get(pk=pk)
        data = json.loads(request.body)
        category.category_name = data.get('category_name')
        category.slug = slugify(data.get('category_name')) + '-' + str(category.id)
        category.description = data.get('category_description')
        category.save()
        return JsonResponse({'message': 'Category updated successfully!', 'alert': 'success'}, status=200)
    except Category.DoesNotExist:
        return JsonResponse({'message': 'Category not found!', 'alert': 'danger'}, status=404)


def menu_edit(request, pk):
    menu = get_object_or_404(Category, pk=pk)
    ctx = {
        'menu': menu
    }
    return render(request, 'vendor/vendor_menu_edit_detail.html', ctx)


@csrf_exempt
@login_required
def menu_delete_detail(request, pk):
    if request.method == 'DELETE':
        category = Category.objects.get(pk=pk)
        category.delete()
        messages.success(request, 'Category deleted successfully')
    return JsonResponse({'message': 'Category deleted successfully!', 'alert': 'success'}, status=200)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def food_item_detail(request, pk):
    try:

        print('request.body', request.POST)
        food = FoodItem.objects.get(pk=pk)

        # Lấy các trường từ request.POST
        food.food_name = request.POST.get('food_name')
        food.food_title = request.POST.get('food_title')
        food.sub_food_title = request.POST.get('food_sub_title')
        food.description = request.POST.get('description')
        food.price = Decimal(request.POST.get('price', '0'))
        food.old_price = Decimal(request.POST.get('old_price', '0'))
        food.is_available = request.POST.get('is_available') == 'true'
        category_id = request.POST.get('category')
        food.category = Category.objects.get(pk=category_id)
        if 'image' in request.FILES:
            food.image = request.FILES['image']

        food.save()

        sizes = []
        size_keys = [key for key in request.POST.keys() if key.startswith('sizes[')]
        for key in size_keys:
            index = key.split('[')[1].split(']')[0]
            size_id = request.POST.get(f'sizes[{index}][size_id]')
            price = request.POST.get(f'sizes[{index}][price]')
            sizes.append({'size_id': size_id, 'price': price})
        print('sizes', sizes)
        for size_data in sizes:
            size_id = size_data['size_id']
            price = size_data['price']
            Size.objects.update_or_create(
                id=size_id,
                defaults={'price': price, 'food_item': food}
            )

        return JsonResponse({'message': 'Food updated successfully!', 'alert': 'success'}, status=200)
    except FoodItem.DoesNotExist:
        return JsonResponse({'message': 'Food not found!', 'alert': 'danger'}, status=404)
    except Exception as e:
        return JsonResponse({'message': str(e), 'alert': 'danger'}, status=500)


@csrf_exempt
@login_required
def food_item_delete(request, pk):
    if request.method == 'DELETE':
        food = FoodItem.objects.get(pk=pk)
        size = Size.objects.filter(food_item=food)
        for s in size:
            s.delete()
        food.delete()
        messages.success(request, 'Food deleted successfully')
    return JsonResponse({'message': 'Food deleted successfully!', 'alert': 'success'}, status=200)


def get_google_api(request):
    return {'GOOGLE_API_KEY': settings.GOOGLE_API_KEY}


def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor


# def opening_hours(request):
#     opening_hours = OpeningHour.objects.filter(vendor=get_vendor(request))
#     form = OpeningHourForm()
#     context = {
#         'form': form,
#         'opening_hours': opening_hours,
#     }
#     return render(request, 'vendor/opening_hours.html', context)

@login_required
def order_detail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order, fooditem__vendor=get_vendor(request))

        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': order.get_total_by_vendor()['subtotal'],
            'tax_data': order.get_total_by_vendor()['tax_dict'],
            'grand_total': order.get_total_by_vendor()['grand_total'],
        }
    except:
        return redirect('vendor')
    return render(request, 'vendor/order_detail.html', context)

@login_required
def my_orders(request):
    vendor = Vendor.objects.get(user=request.user)
    food_items = vendor.vendor_food_items.all()
    ordered_foods = OrderedFood.objects.filter(fooditem__in=food_items)
    orders = Order.objects.filter(id__in=ordered_foods.values('order_id'), is_ordered=True).order_by('-updated_at')
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
        print('order_details_copy', order.user)
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
            'updated_at': order.updated_at,
        }

        for item in order_data['order_details']:
            food_item = FoodItem.objects.get(id=item['food_item'])
            item['food_name'] = food_item.food_name
            item['food_title'] = food_item.food_title
            item['size'] = sizes_cache.get(item['size_id'])
            item['vendor'] = vendors_cache.get(food_item.vendor_id)

        orders_with_details.append(order_data)
    context = {
        'order_statuses': order_statuses,
        'vendor': vendor,
        'orders': orders_with_details,
    }
    return render(request, 'vendor/my_orders.html', context)

@login_required
def request_orders(request):
    from employee.views import check_role_vendor, get_pending_orders_for_vendor

    user = request.user
    vendor = Vendor.objects.get(user=user)
    print('owner_dashboard', vendor)
    pending_orders = get_pending_orders_for_vendor(vendor.id)
    context = {
        'vendor': vendor,
        'pending_orders': pending_orders,
    }

    return render(request, 'vendor/request_order.html', context)


def get_all_orders_res(vendor_id):
    from employee.views import get_order_details

    pending_orders = Order.objects.filter(
        vendors=vendor_id,
    ).select_related('user', 'payment')
    print('pending_orders', pending_orders)
    return get_order_details(pending_orders)


@login_required
def toggle_favorite(request, vendor_id):
    try:
        print('vendor_id', vendor_id)
        vendor = Vendor.objects.get(id=vendor_id)

        favorite, created = Favorite.objects.get_or_create(user=request.user, vendor=vendor)
        print('favorite', favorite, created)
        if not created:
            favorite.delete()  # Xóa nếu đã tồn tại
            return JsonResponse({'status': 'removed'}, status=200)
        return JsonResponse({'status': 'added'}, status=200)
    except Vendor.DoesNotExist:
        return JsonResponse({'error': 'Vendor not found'}, status=404)


@login_required()
def opening_hours(request):
    vendor_time_open = OpeningHour.objects.filter(vendor=get_vendor(request))
    form = OpeningHourForm()
    context = {
        'form': form,
        'vendor_time_open': vendor_time_open,
    }
    return render(request, 'vendor/opening_hour.html', context)


@login_required
def opening_hours_add(request):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            form = OpeningHourForm(request.POST)
            if form.is_valid():

                opening_hour = form.save(commit=False)
                opening_hour.vendor = get_vendor(request)
                opening_hour.save()
                if opening_hour.is_closed:
                    response = {
                        'message': 'Opening hour added successfully!',
                        'status': 'success',
                        'id': opening_hour.id,
                        'day': opening_hour.get_day_display(),
                        'is_closed': 'Closed',

                    }
                else:
                    response = {
                        'message': 'Opening hour added successfully!',
                        'status': 'success',
                        'id': opening_hour.id,
                        'day': opening_hour.get_day_display(),
                        'from_hour': opening_hour.from_hour,
                        'to_hour': opening_hour.to_hour,
                    }
                return JsonResponse(response, status=200)
            return JsonResponse({'message': 'Opening hour not added!', 'alert': 'danger'}, status=400)
    return HttpResponse('opening_hours_add')


def opening_hours_edit(request, pk):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            opening_hour = OpeningHour.objects.get(pk=pk)
            print('opening_hour', opening_hour)
            print('request.POST', request.POST)
            form = OpeningHourForm(request.POST, instance=opening_hour)
            if form.is_valid():
                opening_hour = form.save(commit=False)
                opening_hour.save()
                if opening_hour.is_closed:
                    response = {
                        'message': 'Opening hour updated successfully!',
                        'status': 'success',
                        'id': opening_hour.id,
                        'day': opening_hour.get_day_display(),
                        'is_closed': 'Closed',
                    }
                else:
                    response = {
                        'message': 'Opening hour updated successfully!',
                        'status': 'success',
                        'id': opening_hour.id,
                        'day': opening_hour.get_day_display(),
                        'from_hour': opening_hour.from_hour,
                        'to_hour': opening_hour.to_hour,
                    }
                return JsonResponse(response, status=200)
            return JsonResponse({'message': 'Opening hour not updated!', 'alert': 'danger'}, status=400)
    return HttpResponse('opening_hours_edit')


@login_required()
@csrf_exempt
def opening_hours_delete(request, pk):
    if request.user.is_authenticated:
        print('request', request)
        print('pk', pk)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'DELETE':
            opening_hour = OpeningHour.objects.get(pk=pk)
            opening_hour.delete()
            return JsonResponse({'message': 'Opening hour deleted successfully!', 'status': 'success'}, status=200)
    return HttpResponse('opening_hours_delete')
