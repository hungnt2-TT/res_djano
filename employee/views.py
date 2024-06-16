from django.contrib import auth
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.mail import message
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.urls import reverse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.http import require_http_methods

from wallet.decorators import verified
from wallet.models import Wallet
from .forms import UserCreationForm, RegisterForm
from .models import Profile


# Create your views here.


def home(request):
    return render(request, 'home.html')


def register(request):
    return render(request, 'account/register.html')


def register_user(request):
    print('register_user333333', request.POST)

    form = RegisterForm(request.POST or None)
    print(form.errors)
    ctx = {
        'form': form
    }
    if request.method == 'POST':
        print('register_user333333', request.POST)
        if request.POST.get('next', '') == 'confirm':
            print('confirm ==', ctx)
            if form.is_valid():
                print('confirm2 ==', ctx.get('form'))
                return render(request, 'account/register_confirm.html', ctx)
        if request.POST.get('next', '') == 'back':
            return render(request, 'account/register.html', ctx)
        # Check for "send" in request.POST
        if request.POST.get('next', '') == 'send':
            print('send ==', ctx)
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = True
                user.save()
                return render(request, 'account/register_save.html', ctx)
    return render(request, 'account/register.html', ctx)


def register_user_confirm(request):
    form = request.POST
    ctx = {
        'form': form
    }
    if request.method == 'POST':
        if request.POST.get('send', '') == 'send':
            print('send ==', ctx)
            return render(request, 'account/register_confirm.html', ctx)
    return render(request, 'account/register_confirm.html', ctx)


def register_user_save(request):
    print(request.POST)  # Add this line to print the POST data

    form = RegisterForm(request.POST or None)

    print('register_user_save')

    ctx = {
        'form': form
    }
    print("form ==", form)
    print('register_user_save', form.is_valid(), request.POST)

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.employee_type = Profile.EMPLOYEE_TYPE_OWNER
            return render(request, 'account/register_save.html', ctx)
        else:
            print(form.errors)
    else:
        form = RegisterForm()

    return render(request, 'account/register.html', ctx)  # Add this line


@login_required
@verified
def dashboard(request):
    wallet = get_object_or_404(Wallet, user=request.user)
    return render(request, "dashboard.html", context={"wallet": wallet})


class LoginResView(LoginView):
    def post(self, form):
        form = self.get_form()
        print('form =========', form)
        user = self.request.POST.get('username', '')
        password = self.request.POST.get('password', '')
        print('user =========', user, password)
        user = authenticate(username=user, password=password)
        print('user ==========', user)
        if user:
            if user.is_staff:
                print('user.is_staff')
                form.add_error(None, 'You are not allowed to login here')
                return redirect('home')
        print('form.is_valid()', form.is_valid())
        if form.is_valid():
            print('form.is_valid')

            self.request.session['member_last_login'] = True if user and user.last_login else False
            return self.form_valid(form)
        return self.form_invalid(form)

    def get_success_url(self):
        return reverse('home')


@require_http_methods(["GET", "POST"])
@login_required
def logout_user(request):
    logout(request)
    return redirect("accounts:login")
