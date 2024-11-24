from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)

from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, UserCreationForm, PasswordChangeForm

from vendor.models import Vendor, VendorService, OpeningHour


class VendorForm(forms.ModelForm):
    vendor_type = forms.ChoiceField(choices=Vendor.VENDOR_TYPE_CHOICES, required=False)
    vendor_name = forms.CharField(max_length=50, required=False)

    class Meta:
        model = Vendor
        fields = ['vendor_license', 'fax_number', 'state', 'city', 'longitude', 'latitude', 'address_line_1', 'vendor_tax_code', 'vendor_id_card']

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
        fields = ['fax_number', 'state', 'city', 'longitude', 'latitude', 'address_line_1', 'pin_code', 'street_number']

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


class OpeningHourForm(forms.ModelForm):
    class Meta:
        model = OpeningHour
        fields = ['day', 'from_hour', 'to_hour', 'is_closed']

    def clean(self):
        cleaned_data = super().clean()
        from_hour = cleaned_data.get('from_hour')
        to_hour = cleaned_data.get('to_hour')
        is_closed = cleaned_data.get('is_closed')

        if not is_closed and from_hour and to_hour and from_hour >= to_hour:
            self.add_error('from_hour', 'From hour must be less than to hour.')
            self.add_error('to_hour', 'To hour must be greater than from hour.')
