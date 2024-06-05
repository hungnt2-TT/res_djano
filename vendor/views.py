from django.shortcuts import render

from employee.forms import RegisterForm
from vendor.forms import VendorForm


# Create your views here.
def register_vendor(request):
    form = RegisterForm(request.POST or None)
    vendor_form = VendorForm()
    ctx = {
        "form": form,
        "vendor_form": vendor_form,
    }
    if request.method == 'POST':
        if request.POST.get('next', '') == 'confirm':
            if form.is_valid() and vendor_form.is_valid():
                return render(request, 'vendor/register_confirm.html', ctx)
        if request.POST.get('next', '') == 'back':
            return render(request, 'user_regist.html', ctx)
        if request.POST.get('next', '') == 'send':
            if form.is_valid() and vendor_form.is_valid():
                user = form.save(commit=False)
                user.is_active = True
                user.save()
                vendor = vendor_form.save(commit=False)
                vendor.user = user
                vendor.save()
                return render(request, 'vendor/register_save.html', ctx)

    return render(request, 'vendor/register_vendor.html', ctx)
