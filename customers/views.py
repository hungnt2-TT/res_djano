from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from customers.forms import CustomerForm, UserProfileForm, UserInfoForm
from employee import models as AccountModels
from django.contrib import messages

from django.shortcuts import render, redirect, get_object_or_404

from employee.models import Profile, EmployeeProfile


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
