from django.shortcuts import render

from customers.forms import CustomerForm
from employee import models as AccountModels

from django.shortcuts import render, redirect, get_object_or_404


# Create your views here.
def cprofile(request):
    return render(request, 'customers/profile.html')


def customer_setting(request):
    profile = get_object_or_404(AccountModels.Profile, user=request.user)
    emp_forms = CustomerForm(instance=profile)
    return render(request, 'customers/customer_setting.html')
