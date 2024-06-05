from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)

from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, UserCreationForm, PasswordChangeForm

from vendor.models import Vendor


class VendorForm(forms.ModelForm):

    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license']
        error_messages = {
            'vendor_name': {
                'required': 'This field is required'
            },
            'vendor_license': {
                'required': 'This field is required'
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['vendor_name'].widget.attrs['class'] = 'form-control'
        self.fields['vendor_name'].widget.attrs['placeholder'] = 'Vendor Name'
        self.fields['vendor_license'].widget.attrs['class'] = 'form-control'
        self.fields['vendor_license'].widget.attrs['placeholder'] = 'Vendor License'
