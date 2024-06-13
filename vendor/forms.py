from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)

from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, UserCreationForm, PasswordChangeForm

from vendor.models import Vendor


class VendorForm(forms.ModelForm):
    vendor_type = forms.ChoiceField(choices=Vendor.VENDOR_TYPE_CHOICES, required=False)
    vendor_name = forms.CharField(max_length=50, required=False)

    class Meta:
        model = Vendor
        fields = ['vendor_license', 'fax_number', ]

    def clean(self):
        cleaned_data = super().clean()
        next_action = self.data.get('next', '')
        vendor_type = cleaned_data.get('vendor_type')

        if next_action != 'confirm' and not vendor_type:
            self.add_error('vendor_type', 'This field is required.')
