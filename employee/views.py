from django.shortcuts import render, redirect

from .forms import UserCreationForm, RegisterForm
from .models import Profile


# Create your views here.


def home(request):
    return render(request, 'home.html')


def register(request):
    return render(request, 'account/register.html')


def register_user(request):
    form = RegisterForm(request.POST or None)
    ctx = {
        'form': form
    }
    # print("form =111 ", form, form.is_valid(), request.POST)
    # if request.method == 'POST' and form.is_valid():
    #     print("post = ")
    #     if request.POST.get('next', '') == 'confirm':
    #         # return redirect('register_confirm')
    #         return render(request, 'account/register_confirm.html', ctx)
    #     # if request.POST.get('next', '') == 'send':
    #     #     user = form.save(commit=False)
    #     #     user.is_active = True
    #     #     user.employee_type = Profile.EMPLOYEE_TYPE_OWNER
    #     #     return render(request, 'account/register.html', ctx)
    # print("111111111111111")
    return render(request, 'account/register.html', ctx)


def register_user_confirm(request):
    form = request.POST
    ctx = {
        'form': form
    }
    if request.method == 'POST':
        if request.POST.get('send', '') == 'send':
            print('123123')
            # user = form.save(commit=False)
            # user.is_active = True
            # print("user = ", user)
            # user.employee_type = Profile.EMPLOYEE_TYPE_OWNER
            return render(request, 'account/register_confirm.html', ctx)
    return render(request, 'account/register_confirm.html', ctx)


def register_user_save(request):
    form = RegisterForm(request.POST or None)

    print('register_user_save')

    ctx = {
        'form': form
    }
    print("form ==", form)
    print('register_user_save', form.is_valid(), request.POST)

    if request.method == 'POST':
        if request.POST.get('confirm', '') == 'confirm' and form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.employee_type = Profile.EMPLOYEE_TYPE_OWNER
            print('-----------------------------------')
            return render(request, 'account/register_confirm.html', ctx)

    return render(request, 'account/register_confirm.html', ctx)

