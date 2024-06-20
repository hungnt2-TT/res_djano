from time import sleep

from django.contrib import auth, messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordContextMixin, PasswordResetCompleteView, \
    PasswordResetConfirmView, PasswordChangeView, PasswordChangeDoneView
from django.core.exceptions import PermissionDenied
from django.core.mail import message
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.urls import reverse, reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _

from vendor.forms import VendorForm
from vendor.models import Vendor
from vendor.views import upload_file, render_file_img
from wallet.decorators import verified
from wallet.models import Wallet
from .forms import UserCreationForm, RegisterForm, MyPasswordResetForm, MySetPasswordForm, EmployeeProfileForm
from .mails import send_verification_email
from .models import Profile, EmployeeProfile
from .utils import detect_usertype


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
                user.save()
                send_verification_email(request, user)
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

    ctx = {
        'form': form
    }

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.employee_type = Profile.EMPLOYEE_TYPE_OWNER
            return render(request, 'account/register_save.html', ctx)
        else:
            print(form.errors)
    else:
        return render(request, 'account/register.html', ctx)

    return render(request, 'account/register.html', ctx)  # Add this line


@login_required
@verified
def dashboard(request):
    wallet = get_object_or_404(Wallet, user=request.user)
    return render(request, "dashboard.html", context={"wallet": wallet})


class LoginResView(LoginView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().get(request, *args, **kwargs)

    def post(self, form):

        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        print('LoginResView', self.request.POST)
        if self.request.user.is_authenticated:
            print('You are already logged in')
            messages.warning(self.request, 'You are already logged in')
            return redirect('home')
        form = self.get_form()
        user = self.request.POST.get('username', '')
        password = self.request.POST.get('password', '')
        user = authenticate(username=user, password=password)
        if user:
            if user.is_staff:
                form.add_error(None, 'You are not allowed to login here')
                return self.form_invalid(form)

        if form.is_valid():
            messages.success(self.request, 'You are now logged in')
            self.request.session['member_last_login'] = True if user and user.last_login else False
            return self.form_valid(form)
        return self.form_invalid(form)
    # def get_success_url(self):
    #     return reverse('home')


@require_http_methods(["GET", "POST"])
@login_required
def logout_user(request):
    logout(request)
    return redirect("accounts:login")


class PasswordReset(PasswordResetView):
    subject_template_name = 'account/password_reset_subject.txt'
    success_url = reverse_lazy('ep_password_reset_done')
    form_class = MyPasswordResetForm
    email_template_name = 'account/password_reset_message.txt'
    template_name = 'password_reset_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.user.username
        return context

    def form_valid(self, form):
        users = form.get_users(form.cleaned_data['email'])
        if users:
            user = users[0]
            form.user = user
            return super().form_valid(form)
        else:
            print('No users found with this email')
        return self.form_invalid(form)


class PasswordResetDoneView(PasswordContextMixin, TemplateView):
    template_name = 'password_reset_done.html'
    title = _('Password reset sent')


class PasswordResetComplete(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'
    title = _('Password reset complete')


class PasswordResetConfirm(PasswordResetConfirmView):
    form_class = MySetPasswordForm
    fields = ('new_password1', 'new_password2')
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('ep_password_reset_complete')

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields['new_password1'].widget.attrs['placeholder'] = '半角英数字記号8桁以上'
        form.fields['new_password2'].widget.attrs['placeholder'] = '半角英数字記号8桁以上'

        return form

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     if 'user' in kwargs and 'data' in kwargs and kwargs['data'].get('new_password1'):
    #         kwargs['data']['new_password1'] = kwargs['data']['new_password1'].strip()
    #         kwargs['data']['new_password2'] = kwargs['data']['new_password2'].strip()
    #     return kwargs


def check_role_vendor(user):
    if user.employee_type == 1:
        return True
    else:
        raise PermissionDenied


def check_role_employee(user):
    if user.employee_type == 2:
        return True
    else:
        raise PermissionDenied


@login_required(redirect_field_name='next', login_url='_login')
def middleware_account(request):
    user_type = request.user
    redirect_url = detect_usertype(user_type)
    return redirect(redirect_url)


@login_required(redirect_field_name='next', login_url='_login')
@user_passes_test(check_role_vendor, login_url='_login')
def owner_dashboard(request):
    return render(request, 'owner.html')


@login_required(redirect_field_name='next', login_url='_login')
@user_passes_test(check_role_employee, login_url='_login')
def customer_dashboard(request):
    return render(request, 'customer.html')


def activate(request, uidb64, token):
    args = {

    }

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Profile.objects.get(pk=uid)
        args['user'] = user
    except(TypeError, ValueError, OverflowError, Profile.DoesNotExist):
        user = None
        messages.error(request, 'Activation link is invalid')
    print('activate', user.employeeprofile.email_is_confirmed)
    if user is not None and default_token_generator.check_token(user, token):
        if not user.employeeprofile.email_is_confirmed:
            user.is_active = True
            user.save()

            emprf = user.employeeprofile
            emprf.email_is_confirmed = True
            emprf.save()

            # send email
            send_verification_email(request, user)
            # user_activate_mail(request, user)
            login(request, user)
            messages.success(request, 'Account has been activated')
            return redirect('home')
        else:
            messages.success(request, 'Account is already activated')
            return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid')
        return redirect('login')


def history(request):
    return render(request, 'history.html')


class PasswordChange(PasswordChangeView):
    form_class = MySetPasswordForm
    template_name = 'password_change.html'
    success_url = reverse_lazy('p_password_change_done')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if 'data' in kwargs:
            profile = self.request.user.employeeprofile
            profile.password = kwargs['data']['new_password1']
            profile.save()
        return kwargs


class PasswordChangeDone(PasswordChangeDoneView):
    template_name = 'password_change_done.html'


def vendor_profile_update(request):
    # get data instance to form
    profile = get_object_or_404(EmployeeProfile, user=request.user)
    profile = get_object_or_404(EmployeeProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    vendor_forms = VendorForm(instance=vendor)

    print('request.user', request.user)
    img_logo = render_file_img(request, profile.profile_picture)
    img_cover = render_file_img(request, profile.cover_photo)

    print('vendor_profile_update', profile)
    print('vendor_profile_update', vendor)
    emp_forms = EmployeeProfileForm(instance=profile)
    ctx = {
        'vendor_forms': vendor_forms,
        'emp_forms': emp_forms,
        'img_cover': img_cover,
        'img_logo': img_logo,
    }
    return render(request, 'vendor/vendor_profile_update.html', ctx)
