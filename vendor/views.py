from django.shortcuts import render

from employee.forms import RegisterForm, RegisterEmployeeProfile
from vendor.forms import VendorForm
from django.conf import settings
import os

from vendor.models import Vendor


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


def get_type_vendor():
    vendor_type = Vendor.VENDOR_TYPE_CHOICES
    return vendor_type


def handle_confirm(request, form, vendor_form, profile_form):
    print('form_data', request.POST, form.errors, vendor_form.errors, profile_form.errors)
    if form.is_valid() and vendor_form.is_valid():
        request.session['form_data'] = request.POST.copy()
        vendor_type = get_type_vendor()
        return render(request, 'vendor/register_vendor_package.html', {
            "form": form,
            "vendor_form": vendor_form,
            "profile_form": profile_form,
            "vendor_type": vendor_type,
        })
    return render(request, 'vendor/register_vendor.html', {
        "form": form,
        "vendor_form": vendor_form,
        "profile_form": profile_form,
    })

def handle_back(request, form, vendor_form, profile_form):
    return render(request, 'vendor/register_vendor.html', {
        "form": form,
        "vendor_form": vendor_form,
        "profile_form": profile_form,
    })


def handle_next_payment(request, form, vendor_form, profile_form):
    print('request.POST', request.POST, form.errors, vendor_form.errors, profile_form.errors)
    form_data = request.session.get('form_data', {})
    print('form_data', form_data)
    vendor_type_value = request.POST.get('vendor_type', '')
    if vendor_type_value.isdigit():
        form_data.update({'vendor_type': int(vendor_type_value)})
    # form_data.update(request.POST.get('vendor_type', ''))
    print('form_data', form_data, form_data, request.POST, form.errors, vendor_form.errors)
    if form.is_valid() and vendor_form.is_valid():
        user = form.save(commit=False)
        user.is_active = True
        user.employee_type = 2
        user.save()
        print('user = ', user)
        vendor = vendor_form.save(commit=False)
        vendor.user = user
        user_profile = user.employee_type
        vendor.user_profile = user_profile
        vendor.save()
        return render(request, 'vendor/register_vendor_send.html', {
            "form": form,
            "vendor_form": vendor_form,
            "profile_form": profile_form,
        })
    return render(request, 'vendor/register_vendor.html',{
        "form": form,
        "vendor_form": vendor_form,
        "profile_form": profile_form,
    })


def register_vendor(request):
    print('request =', request.POST)
    form_data = request.session.get('form_data', {})

    upload_file_url = upload_file(request.FILES.get('vendor_license'))
    profile_form = RegisterEmployeeProfile(request.POST or None)
    form = RegisterForm(request.POST or None)
    vendor_form = VendorForm(request.POST or None)

    if request.method == 'POST':
        next_action = request.POST.get('next', '')
        if next_action == 'confirm':
            return handle_confirm(request, form, vendor_form, profile_form)
        elif next_action == 'back':
            return handle_back(request, form, vendor_form, profile_form)
        elif next_action == 'next_payment':
            print('next_payment')
            return handle_next_payment(request, form, vendor_form, profile_form)

    return render(request, 'vendor/register_vendor.html', {
        "form": form,
        "vendor_form": vendor_form,
        "profile_form": profile_form,
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
