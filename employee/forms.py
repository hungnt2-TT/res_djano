from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, UserCreationForm, PasswordChangeForm

from employee.models import CustomProfile, Profile, EmployeeProfile


class RegisterForm(UserCreationForm):
    class Meta:
        model = Profile
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['email'].widget.attrs['placeholder'] = 'Requires entering correct email structure'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password (min 8 characters)'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None


# class RegisterEmployeeProfile(forms.ModelForm):
#     class Meta:
#         model = EmployeeProfile
#         fields = ['state', 'city', 'longitude', 'latitude', 'address_line_1']
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field in self.fields.values():
#             field.widget.attrs['class'] = 'form-control'
#         self.fields['state'].widget.attrs['placeholder'] = 'State'
#         self.fields['city'].widget.attrs['placeholder'] = 'City'
#         self.fields['address_line_1'].widget.attrs['placeholder'] = 'Address '
# def __init__(self, *args, **kwargs):

class MyPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(MyPasswordResetForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'

    def clean_email(self):
        email = self.cleaned_data['email']
        profile = Profile.objects.filter(email__iexact=email, is_active=True)
        if not len(profile):
            raise forms.ValidationError('There is no user associated with this email address')
        return email

    def send_mail(
            self,
            subject_template_name,
            email_template_name,
            context,
            from_email,
            to_email,
            html_email_template_name=None,
    ):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()

    def get_users(self, email):
        active_users = get_user_model()._default_manager.filter(
            email__iexact=email, is_active=True)
        return active_users


class MySetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(MySetPasswordForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = None
            field.widget.attrs['placeholder'] = field.label


class EmployeeProfileForm(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = ['profile_picture', 'cover_photo', 'email_is_confirmed']

    def __int__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['profile_picture'].widget.attrs['placeholder'] = 'Profile Picture'
        self.fields['cover_photo'].widget.attrs['placeholder'] = 'Cover Photo'
        self.fields['email_is_confirmed'].widget.attrs['placeholder'] = 'Email is Confirmed'
