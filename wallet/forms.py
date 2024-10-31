from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.forms import NumberInput

from wallet.models import PaymentMethod


class BVNForm(forms.Form):
    bvn = forms.CharField(
        widget=NumberInput(attrs={'class': 'form-control', 'placeholder': 'Your BVN', 'required': 'required'}))


class PaymentForm(forms.Form):
    class Meta:
        model = PaymentMethod
        fields = ['card_number', 'expiry_date', 'cvv', 'payment_method']

    card_number = forms.CharField(
        widget=NumberInput(attrs={'class': 'form-control', 'placeholder': 'Card Number', 'required': 'required'}))


class VnpayPaymentForm(forms.Form):

    order_id = forms.CharField(max_length=250)
    order_type = forms.CharField(max_length=20)
    amount = forms.IntegerField()
    order_desc = forms.CharField(max_length=100)
    bank_code = forms.CharField(max_length=20, required=False)
    language = forms.CharField(max_length=2)