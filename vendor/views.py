from django.contrib import messages
from django.shortcuts import render, redirect

from employee.forms import RegisterForm
from employee.models import EmployeeProfile, Profile
from vendor.forms import VendorForm
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


# Create your views here.
# def register_vendor(request):
#     print('(request)', request)
#     if 'vendor_license' in request.FILES:
#         upload_file_url = upload_file(request.FILES['vendor_license'])
#     else:
#         upload_file_url = None
#     print('register_user333333', request.POST, request.FILES)
#     profile_form = RegisterEmployeeProfile(request.POST or None)
#     form = RegisterForm(request.POST or None)
#     vendor_form = VendorForm(request.POST or None)
#
#     ctx = {
#         "form": form,
#         "vendor_form": vendor_form,
#         "profile_form": profile_form
#     }
#
#     ctx['upload_file_url'] = upload_file_url
#     print('fomr.errors', form.errors, vendor_form.errors, profile_form.errors)
#     if request.method == 'POST':
#         if request.POST.get('next', '') == 'confirm':
#             if form.is_valid() and vendor_form.is_valid():
#                 request.session['form_data'] = request.POST
#
#                 vendor_type = get_type_vendor()
#                 ctx['vendor_type'] = vendor_type
#                 return render(request, 'vendor/register_vendor_package.html', ctx)
#         if request.POST.get('next', '') == 'back':
#             return render(request, 'vendor/register_vendor.html', ctx)
#         if request.POST.get('next', '') == 'next_payment':
#             form_data = request.session.get('form_data', {})
#             form_data.update(request.POST)
#             if form.is_valid() and vendor_form.is_valid():
#                 user = form.save(commit=False)
#                 user.is_active = True
#                 user.employee_type = 2
#                 user.save()
#                 vendor = vendor_form.save(commit=False)
#                 vendor.user = user
#                 user_profile = user.profile
#                 vendor.user_profile = user_profile
#                 vendor.save()
#                 return render(request, 'vendor/register_save.html', ctx)
#
#     return render(request, 'vendor/register_vendor.html', ctx)


def get_google_api(request):
    return {'GOOGLE_API_KEY': settings.GOOGLE_API_KEY}
