from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.forms import NumberInput


class BVNForm(forms.Form):
    bvn = forms.CharField(
        widget=NumberInput(attrs={'class': 'form-control', 'placeholder': 'Your BVN', 'required': 'required'}))
