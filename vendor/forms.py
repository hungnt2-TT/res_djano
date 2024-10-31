from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)

from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, UserCreationForm, PasswordChangeForm

from vendor.models import Vendor, VendorService


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['state'].widget.attrs['placeholder'] = 'State'
        self.fields['city'].widget.attrs['placeholder'] = 'City'
        self.fields['address_line_1'].widget.attrs['placeholder'] = 'Address '
        self.fields['vendor_name'].widget.attrs['placeholder'] = 'Vendor Name'
        self.fields['fax_number'].widget.attrs['placeholder'] = 'Fax Number'


class VendorUpdateMapForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['fax_number', 'state', 'city', 'longitude', 'latitude', 'address_line_1', 'pin_code', 'location', 'street_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['state'].widget.attrs['placeholder'] = 'State'
        self.fields['state'].widget.attrs['id'] = 'administrative_area_level_2'
        self.fields['city'].widget.attrs['placeholder'] = 'City'
        self.fields['city'].widget.attrs['id'] = 'administrative_area_level_1'
        self.fields['address_line_1'].widget.attrs['placeholder'] = 'Address '
        self.fields['address_line_1'].widget.attrs['id'] = 'route'
        self.fields['fax_number'].widget.attrs['placeholder'] = 'Fax Number'
        self.fields['pin_code'].widget.attrs['placeholder'] = 'Pin Code'
        self.fields['pin_code'].widget.attrs['id'] = 'postal_code'
        self.fields['location'].widget.attrs['placeholder'] = 'Location'
        self.fields['street_number'].widget.attrs['placeholder'] = 'Street number'
        self.fields['street_number'].widget.attrs['id'] = 'street_number'


class VendorServiceForm(forms.ModelForm):
    class Meta:
        model = VendorService
        fields = ['pre_order', 'pre_order_days', 'pre_order_hours', 'delivery_available', 'delivery_fee',
                  'payment_on_delivery', 'booking']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pre_order'].widget = forms.Select(choices=[('no', 'No'), ('yes', 'Yes')])
        self.fields['delivery_available'].widget = forms.Select(choices=[('no', 'No'), ('yes', 'Yes')])
        self.fields['payment_on_delivery'].widget = forms.Select(choices=[('no', 'No'), ('yes', 'Yes')])
        self.fields['booking'].widget = forms.Select(choices=[('no', 'No'), ('yes', 'Yes')])

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['pre_order'].widget.attrs['placeholder'] = 'Pre Order'
        self.fields['pre_order_days'].widget.attrs['placeholder'] = 'Pre Order Days'
        self.fields['pre_order_hours'].widget.attrs['placeholder'] = 'Pre Order Hours'
        self.fields['delivery_available'].widget.attrs['placeholder'] = 'Delivery Available'
        self.fields['delivery_fee'].widget.attrs['placeholder'] = 'Delivery Fee'
        self.fields['payment_on_delivery'].widget.attrs['placeholder'] = 'Payment On Delivery'
        self.fields['booking'].widget.attrs['placeholder'] = 'Booking'
