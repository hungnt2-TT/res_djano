from django.shortcuts import render

from employee.forms import RegisterForm
from vendor.forms import VendorForm


# Create your views here.
def register_vendor(request):
    print("request.FILES['filename'].name", request.FILES)
    print('register_user333333', request.POST, request.FILES)
    vendor_license_filename = request.POST.get('vendor_license', '')

    form = RegisterForm(request.POST or None)
    vendor_form = VendorForm(request.POST or None, request.FILES or None)
    ctx = {
        "form": form,
        "vendor_form": vendor_form,
        "vendor_license_filename": vendor_license_filename,
    }
    print('register_user333333', ctx)
    if request.method == 'POST':
        if request.POST.get('next', '') == 'confirm':
            if form.is_valid() and vendor_form.is_valid():
                return render(request, 'vendor/register_vendor_cf.html', ctx)
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
