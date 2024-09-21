from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, UserCreationForm, PasswordChangeForm

from employee.models import CustomProfile, Profile, EmployeeProfile
from employee.validators import validator_file_upload
from django.core.validators import RegexValidator


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


class RegisterFormByEmail(UserCreationForm):
    phone_number = forms.RegexField(regex=r"^(84|0[3|5|7|8|9])+([0-9]{8})\b",
                                    max_length=10,
                                    required=False, label='Phone Number',
                                    error_messages={

                                        'invalid':"※The phone number must start with 84 or 0[3|5|7|8|9]."
                                    })

    class Meta:
        model = Profile
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number', 'verified']

    def __init__(self, *args, **kwargs):
        phone_number = kwargs.pop('phone_number', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['email'].widget.attrs['placeholder'] = 'Requires entering correct email structure'
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['password1'].widget.attrs['placeholder'] = 'Password (min 8 characters)'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Phone Number'
        if phone_number:
            self.fields['phone_number'].initial = phone_number


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
    profile_picture = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'placeholder': 'Profile Picture'}),
        validators=[validator_file_upload])
    cover_photo = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control', 'placeholder': 'Cover Photo'}),
                                  validators=[validator_file_upload])

    class Meta:
        model = EmployeeProfile
        fields = ['profile_picture', 'cover_photo', 'email_is_confirmed', 'user']

    def __int__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print('self.fields', self.fields)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['email_is_confirmed'].widget.attrs['placeholder'] = 'Email is Confirmed'


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'nickname', 'username', 'email_contact']

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = None
            field.widget.attrs['placeholder'] = field.label
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
