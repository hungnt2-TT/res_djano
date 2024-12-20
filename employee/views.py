import os
from django.db.models import Q

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordContextMixin, PasswordResetCompleteView, \
    PasswordResetConfirmView, PasswordChangeView, PasswordChangeDoneView
from django.contrib.gis.geos import Point
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from google.auth.transport import requests
from google.oauth2 import id_token

from menu.models import FoodItem
from vendor.forms import VendorUpdateForm, VendorServiceForm
from vendor.models import Vendor
from vendor.views import render_file_img
from wallet.decorators import verified
from wallet.models import Wallet
from .forms import RegisterForm, MyPasswordResetForm, MySetPasswordForm, EmployeeProfileForm, \
    ProfileUpdateForm, RegisterFormByEmail
from .mails import send_verification_email
from .models import Profile, EmployeeProfile, District
from .utils import detect_usertype
from datetime import datetime

from twilio.rest import Client

from django.contrib.auth.models import AnonymousUser

from django.core.serializers import serialize

from django.contrib.gis.geos import Point


def home(request):
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    if request.user.is_authenticated:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True).exclude(user=request.user)
    else:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendors_premium = vendors.filter(vendor_type=Vendor.VENDOR_TYPE_PREMIUM)
    profile = Profile.objects.filter(is_active=True)

    information = {
        'vendors': vendors.count(),
        'profile': profile.count()
    }
    current_hour = datetime.now().hour + 7
    print('current_hour', current_hour)
    if 6 <= current_hour < 12:
        time_range = 'morning'
    elif 12 <= current_hour < 18:
        time_range = 'afternoon'
    elif 18 <= current_hour < 24:
        time_range = 'evening'
    else:
        time_range = 'night'

    food_items = FoodItem.objects.filter(time_range=time_range)
    vendors_list = []
    if lat and lng:
        lat = float(lat)
        lng = float(lng)
        user_location = Point(lng, lat, srid=4326)
        if request.user.is_authenticated:
            employee_profile = EmployeeProfile.objects.get(user=request.user)
            employee_profile.latitude = lat
            employee_profile.longitude = lng
            employee_profile.save()
        districts = District.objects.filter(geom__contains=user_location).first()
        print('districts', districts)
        if vendors:
            print('vendors', vendors)
            vendor_district = vendors.filter(name_district=districts)
            print('vendors', vendors)
            vendors_list = list(vendor_district.values())
            for vendor in vendors_list:
                vendor.pop('location', None)

        districts_dict = districts and {
            'id': districts.id,
            'ten_tinh': districts.ten_tinh,
            'ten_huyen': districts.ten_huyen,
            'dan_so': districts.dan_so,
            'nam_tk': districts.nam_tk,
            'code_vung': districts.code_vung,
            # 'location': {'lat': districts.geom.centroid.y, 'lng': districts.geom.centroid.x} if districts.geom else None
        }
        return JsonResponse({
            'vendors': vendors_list if vendors_list else [],
            'information': information,
            'districts': districts_dict,
            'status': 'success',
            'vendors_premium': list(vendors_premium.values())  # Convert QuerySet to list
        })
    else:
        districts = None
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    print('vendors districts', food_items)
    context = {
        'vendors': vendors,
        'districts': districts,
        'lat': lat,
        'lng': lng,
        'information': information,
        'food_items': food_items,
        'vendors_premium': vendors_premium,

        'time_range': time_range
    }
    print('context', context)
    return render(request, 'home.html', context)

def register(request):
    return render(request, 'account/register.html')


def broadcast_sms(phone_number):
    phone_number_vn = '+84' + phone_number
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        verification = client.verify.v2.services(settings.SECRET_KEY_TWILIO).verifications.create(to=phone_number_vn,
                                                                                                  channel='sms')

        print('verification_check', verification)
    except Exception as e:
        print(f'Error verification: {e}')
        verification = None
    return verification


def verification_checks(request, phone_number):
    phone_number = '+84' + phone_number
    code_list = request.POST.getlist('code')
    code = ''.join(code_list)
    print('code', code)
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    try:
        verification_check = client.verify.v2.services(settings.SECRET_KEY_TWILIO).verification_checks.create(
            to=phone_number, code=code)
        print('verification_check', verification_check.status)
    except Exception as e:
        print(f'Error verification check coded: {e}')
        verification_check = None
    return verification_check


def send_sms_view(request, phone_number):
    phone_number_vn = '+84' + phone_number
    if request.method == 'POST':
        code_list = request.POST.getlist('code')
        code = ''.join(code_list)
        print('code', code)
        verify = verification_checks(request, phone_number)
        if verify.status == 'approved' or verify.valid == 'true':
            user = Profile.objects.get(email=request.user.email)
            user.phone_number_verified = True
            user.save()
            return render(request, 'account/register_save.html')
    sms_sid = broadcast_sms(phone_number)

    if sms_sid.status == 'pending':
        messages.success(request, 'Code has been sent. Please check your phone.')
        return render(request, 'send_sms_form.html', {'phone_number': phone_number})
    else:
        messages.error(request, 'Failed to send code.')
    return render(request, 'send_sms_form.html')

def register_user(request):
    form = RegisterForm(request.POST or None)
    ctx = {
        'form': form
    }
    if request.method == 'POST':
        if request.POST.get('next', '') == 'confirm':
            print('confirm ==', ctx)
            if form.is_valid():
                return render(request, 'account/register_confirm.html', ctx)
        if request.POST.get('next', '') == 'send':
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
            return render(request, 'account/register_confirm.html', ctx)
    return render(request, 'account/register_confirm.html', ctx)


def register_user_save(request):
    form = RegisterForm(request.POST or None)
    ctx = {
        'form': form
    }
    print('register_user_save', request.POST)
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.employee_type = Profile.EMPLOYEE_TYPE_CUSTOMER
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
            print('You are already logged in')
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
            user = form.get_user()
            print('user ====', user)
            if user.employee_type == 1:
                try:
                    vendor = get_object_or_404(Vendor, user=user)
                    print('vendor', vendor)
                    if not vendor.is_approved:
                        messages.warning(self.request, 'Your account is not approved yet')
                        raise PermissionDenied
                except Vendor.DoesNotExist:
                    pass

            messages.success(self.request, 'You are now logged in')
            self.request.session['member_last_login'] = True if user and user.last_login else False
            return self.form_valid(form)
        return self.form_invalid(form)
    # def get_success_url(self):
    #     return reverse('home')


def convert_email_to_username(type):
    print('convert_email_to_username', type)
    if type.split('@')[0]:
        user_name = get_object_or_404(Profile, email=type).username
        print('user', user_name)
        return user_name
    return type


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
    print('middleware_account', user_type)
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
    print('vendor_profile_update', request.user)
    print('vendor_profile_update', request.POST)
    profile = EmployeeProfile.objects.get(user=request.user)
    print('profile', profile.profile_picture)
    vendor = Vendor.objects.get(user=request.user)
    if request.method == 'POST':
        print('request.POST', request.POST)
        vendor_forms = VendorUpdateForm(request.POST, instance=vendor)
        vendor_service = VendorServiceForm(request.POST, instance=vendor.vendor_service)
        emp_forms = EmployeeProfileForm(request.POST, request.FILES, instance=profile)
        user = ProfileUpdateForm(request.POST, instance=request.user)
        print('vendor_forms errors =', vendor_service.errors)

        if vendor_forms.is_valid() and emp_forms.is_valid() and user.is_valid() and vendor_service.is_valid():
            print('vendor_forms.cleaned_data', vendor_service.cleaned_data)
            vendor_forms.save()
            print('vendor_service.cleaned_data', vendor_service)
            print('vendor_service.vendor', vendor)

            vendor_service = vendor_service.save(commit=False)
            vendor_service.vendor = vendor
            vendor_service.save()
            try:
                emp = EmployeeProfile.objects.get(user=request.user)
                emp.profile_picture = request.FILES.get('img_logo') if request.FILES.get(
                    'img_logo') else emp.profile_picture
                emp.cover_photo = request.FILES.get('img_cover') if request.FILES.get('img_cover') else emp.cover_photo
                emp.save()
            except Exception as e:
                print('Error when saving user:', e)
            user.save()
            messages.success(request, 'Profile updated successfully')

            return redirect('profile')

    if profile.profile_picture or profile.cover_photo:
        img_logo = render_file_img(request, profile.profile_picture)
        img_cover = render_file_img(request, profile.cover_photo)
    else:
        img_logo = None
        img_cover = None

    vendor_forms = VendorUpdateForm(instance=vendor)
    emp_forms = EmployeeProfileForm(instance=profile)
    vendor_service = VendorServiceForm(instance=vendor.vendor_service)
    print('vendor_service', vendor_service)
    user = ProfileUpdateForm(instance=request.user)
    print('profile.cover_photo', profile.cover_photo)
    print('profile.profile_picture', profile.profile_picture)
    ctx = {
        'vendor_forms': vendor_forms,
        'emp_forms': emp_forms,
        'img_cover': img_cover,
        'img_logo': img_logo,
        'user': user,
        'vendor_service': vendor_service
    }
    return render(request, 'vendor/vendor_profile_update.html', ctx)


@csrf_exempt
def auth_receiver(request):
    """
    Google calls this URL after the user has signed in with their Google account.
    """
    token = request.POST['credential']

    try:
        user_data = id_token.verify_oauth2_token(
            token, requests.Request(), os.getenv('GOOGLE_CLIENT_ID')
        )
        request.session['user_data'] = user_data
        print('user_data auth_receiver', user_data)
        user = Profile.objects.filter(email=user_data['email']).first()
        print('user', user)
        if user:
            print('auth_receiver=', user)
            messages.success(request, 'You are now logged in')
            login(request, user)
            return redirect('home')
        else:
            return redirect('login_by_email')

    except ValueError:
        return HttpResponse(status=403)


def register_by_email(request):
    user_data = request.session.get('user_data', None)
    print('user_data', user_data)
    initial_data = {}
    if user_data:
        initial_data = {'email': user_data['email'],
                        'first_name': user_data['given_name'],
                        'last_name': user_data['family_name'],
                        'email_verified': user_data['email_verified'],
                        'username': user_data['name'],
                        'verified': user_data['email_verified'],
                        }
    form = RegisterFormByEmail(request.POST or None, initial=initial_data)
    form.full_clean()
    if request.method == 'POST':
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.verified = True
            user.save()
            return render(request, 'account/register_save.html')
    context = {'form': form}
    return render(request, 'account/register_by_email.html', context)
    #
    # if request.method == 'POST':
    #     if 'send_code' in request.POST:
    #         if form.is_valid():
    #             request.session['form_data'] = request.POST.dict()
    #             phone_number = form.cleaned_data.get('phone_number')
    #             send_code = broadcast_sms(phone_number)
    #             if send_code.status == 'pending':
    #                 messages.success(request, 'Code has been sent. Please check your phone.')
    #                 return render(request, 'send_sms_form.html', {'phone_number': phone_number})
    #             else:
    #                 messages.error(request, 'Failed to send code.')
    #         else:
    #             messages.error(request, 'Form is not valid.')
    #     elif 'verify' in request.POST:
    #         form_data = request.session.get('form_data', {})
    #         form = RegisterFormByEmail(form_data or None)
    #         phone_number = form_data.get('phone_number')
    #         verify = verification_checks(request, phone_number)
    #         if verify.status == 'approved' or verify.valid == 'true':
    #             user = form.save(commit=False)
    #             user.is_active = True
    #             user.verified = True
    #             user.save()
    #             del request.session['form_data']
    #             return render(request, 'account/register_save.html')
    #         else:
    #             messages.error(request, 'Invalid code.')
    #             return render(request, 'send_sms_form.html', {'form': form})


def update_location(request):
    if request.method == 'POST':
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        address = request.POST.get('address')
        user = request.user
        if user:
            profile = EmployeeProfile.objects.get(user=user)
            profile.latitude = lat
            profile.longitude = lng
            profile.address_line_1 = address
            profile.save()
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'})
