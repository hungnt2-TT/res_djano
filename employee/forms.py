from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)

from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, UserCreationForm, PasswordChangeForm

from employee.models import CustomProfile, Profile


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='First Name')
    last_name = forms.CharField(max_length=30, required=True, help_text='Last Name')

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['last_name'].widget.attrs['autofocus'] = 'autofocus'
        self.fields['password1'].widget.attrs['placeholder'] = '半角英数字記号8桁以上'
        self.fields['password2'].widget.attrs['placeholder'] = '半角英数字記号8桁以上'
