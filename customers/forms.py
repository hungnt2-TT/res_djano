from django import forms

from employee.models import Profile
from employee.validators import validator_file_upload


class CustomerForm(forms.Form):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'phone_number', 'username', 'email', 'nickname', 'employee_type']