from decimal import Decimal
from traceback import print_tb

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import F

from employee import consts
from employee.consts import PAGE
from employee.forms import RegisterForm
from employee.models import EmployeeProfile, Profile
from employee.paginations import paginate_data
from menu.forms import CategoryForm, FoodItemForm, SizeForm
from menu.models import Category, FoodItem, Size
from vendor.forms import VendorForm, VendorUpdateForm, VendorUpdateMapForm
from django.conf import settings
from vendor.models import Vendor
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
        print('form_data', form_data)
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


@login_required
def vendor_map(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    vendor_form = VendorUpdateMapForm(instance=vendor)

    ctx = {
        'vendor_form': vendor_form,
        'initSearchBox': 'initSearchBox'
    }
    if request.method == 'POST':
        vendor_form = VendorUpdateMapForm(request.POST, request.FILES, instance=vendor)
        if vendor_form.is_valid():
            vendor = vendor_form.save()
            if vendor:
                messages.success(request, 'Vendor updated successfully')
                return redirect('vendor_map')
            messages.error(request, 'Vendor not updated')
            return redirect('vendor_map')
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
        print('food_form', food_form)
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
        food.is_available = request.POST.get('is_available') == 'true'

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
