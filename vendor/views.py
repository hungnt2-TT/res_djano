from django.shortcuts import render

from employee.forms import RegisterForm, RegisterEmployeeProfile
from vendor.forms import VendorForm
from django.conf import settings
import os


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


# Create your views here.
def register_vendor(request):
    if 'vendor_license' in request.FILES:
        upload_file_url = upload_file(request.FILES['vendor_license'])
    else:
        upload_file_url = None
    print('register_user333333', request.POST, request.FILES)
    profile_form = RegisterEmployeeProfile(request.POST or None)
    form = RegisterForm(request.POST or None)
    vendor_form = VendorForm(request.POST or None, request.FILES or None)

    ctx = {
        "form": form,
        "vendor_form": vendor_form,
        "profile_form": profile_form
    }

    ctx['upload_file_url'] = upload_file_url
    print('fomr.errors', form.errors, vendor_form.errors, profile_form.errors)
    if request.method == 'POST':
        if request.POST.get('next', '') == 'confirm':
            if form.is_valid() and vendor_form.is_valid():
                print('form.cleaned_data', form.cleaned_data)
                return render(request, 'vendor/register_vendor_package.html', ctx)
        if request.POST.get('next', '') == 'back':
            return render(request, 'vendor/register_vendor.html', ctx)
        if request.POST.get('next', '') == 'send':
            if form.is_valid() and vendor_form.is_valid():
                user = form.save(commit=False)
                user.is_active = True
                user.employee_type = 2
                user.save()
                vendor = vendor_form.save(commit=False)
                vendor.user = user
                user_profile = user.profile
                vendor.user_profile = user_profile
                vendor.save()
                return render(request, 'vendor/register_save.html', ctx)

    return render(request, 'vendor/register_vendor.html', ctx)


def get_google_api(request):
    return {'GOOGLE_API_KEY': settings.GOOGLE_API_KEY}