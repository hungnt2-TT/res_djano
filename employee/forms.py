from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)

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


class RegisterEmployeeProfile(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = ['state', 'city', 'longitude', 'latitude', 'address_line_1']

    # def __init__(self, *args, **kwargs):
