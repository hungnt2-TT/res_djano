from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from employee.forms import RegisterForm
from employee.models import EmployeeProfile, Profile
from menu.models import Category
from vendor.forms import VendorForm, VendorUpdateForm, VendorUpdateMapForm
from django.conf import settings
import os

from vendor.models import Vendor
from wallet.models import Wallet


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
    form_data = request.session.get('form_data', {})
    if form_data:
        user = Profile.objects.create_user(
            username=form_data.get('username', ''),
            email=form_data.get('email', ''),
            password=form_data.get('password1', ''),
            first_name=form_data.get('first_name', ''),
            last_name=form_data.get('last_name', ''),
        )
        user.is_active = True
        user.employee_type = 2
        user.save()

        Wallet.objects.create(user=user, balance=0)
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
            longitude=form_data.get('longitude', ''),
            latitude=form_data.get('latitude', ''),
        )
        return render(request, 'vendor/register_vendor_send.html', {
            "form_data": form_data,
        })
    return redirect('vendor:register_vendor')


def register_vendor(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in')
        return redirect('home')

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


def menu_builder(request):
    vendor = Vendor.objects.get(user=request.user)
    menu = Category.objects.filter(vendor=vendor)
    print('menu= ==', menu)
    ctx = {
        'menus': menu
    }
    return render(request, 'vendor/vendor_menu_builder.html', ctx)


def menu_edit_detail(request, pk):
    menu = get_object_or_404(Category, pk=pk)
    ctx = {
        'menu': menu
    }
    return render(request, 'vendor/vendor_menu_edit_detail.html', ctx)


def menu_delete_detail(request, pk):
    menu = get_object_or_404(Category, pk=pk)
    ctx = {
        'menu': menu
    }
    return render(request, 'vendor/vendor_menu_delete_detail.html', ctx)


def get_google_api(request):
    return {'GOOGLE_API_KEY': settings.GOOGLE_API_KEY}
