from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import Order


class OrderForm(forms.ModelForm):
    phone_regex = RegexValidator(
        regex=r'^(0[3|5|7|8|9])+([0-9]{8})$',
        message="Phone number must start with 03, 05, 07, 08, or 09 and be 10 digits long."
    )
    phone = forms.CharField(validators=[phone_regex], max_length=10)

    pin_code_regex = RegexValidator(
        regex=r'^\d{5,6}$',
        message="PIN code must be 5 or 6 digits for Vietnam."
    )
    pin_code = forms.CharField(validators=[pin_code_regex], max_length=5)

    class Meta:
        model = Order
        fields = ('first_name', 'last_name', 'phone', 'email', 'address', 'country', 'state', 'city', 'pin_code')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email is required.")
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise ValidationError("First name is required.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise ValidationError("Last name is required.")
        return last_name

    def clean_country(self):
        country = self.cleaned_data.get('country')
        print('country', country)
        if country.lower() not in ['vietnam', 'vn', 'việt nam', 'viet nam']:
            raise ValidationError("Currently, we only accept orders from Vietnam.")
        return country

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get('phone')
        email = cleaned_data.get('email')

        if not phone and not email:
            raise ValidationError("Either phone number or email must be provided.")

        return cleaned_data
