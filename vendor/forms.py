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
        fields = ['vendor_license', 'fax_number', 'state', 'city', 'longitude', 'latitude', 'address_line_1']

    def clean(self):
        cleaned_data = super().clean()
        next_action = self.data.get('next', '')
        vendor_type = cleaned_data.get('vendor_type')

        if next_action != 'confirm' and not vendor_type:
            self.add_error('vendor_type', 'This field is required.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['state'].widget.attrs['placeholder'] = 'State'
        self.fields['city'].widget.attrs['placeholder'] = 'City'
        self.fields['address_line_1'].widget.attrs['placeholder'] = 'Address '


class VendorUpdateForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'fax_number', 'state', 'city', 'longitude', 'latitude', 'address_line_1', 'vendor_description']

    def __int__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['state'].widget.attrs['placeholder'] = 'State'
        self.fields['city'].widget.attrs['placeholder'] = 'City'
        self.fields['address_line_1'].widget.attrs['placeholder'] = 'Address '
        self.fields['vendor_name'].widget.attrs['placeholder'] = 'Vendor Name'
        self.fields['fax_number'].widget.attrs['placeholder'] = 'Fax Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Requires entering correct email structure'
