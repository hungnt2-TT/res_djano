from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime
import re

from marketplace.utils import generate_time_choices
from vendor.models import Reservation


class ReservationForm(forms.ModelForm):
    RESERVATION_TIME_CHOICES = generate_time_choices()
    GUESTS = [
        (1, '1 Guest'),
        (2, '2 Guests'),
        (3, '3 Guests'),
        (4, '4 Guests'),
        (5, '5 Guests'),
        (6, '6 Guests'),
        (7, '7 Guests'),
        (8, '8 Guests'),
        (9, '9 Guests'),
        (10, '10 Guests'),
        (11, 'More than 10 Guests')
    ]
    phone_number = forms.CharField(max_length=10)
    reservation_time = forms.ChoiceField(choices=RESERVATION_TIME_CHOICES)
    guest_number = forms.ChoiceField(choices=GUESTS)

    class Meta:

        model = Reservation
        fields = ['vendor', 'user', 'first_name', 'phone_number', 'last_name', 'name', 'email', 'reservation_date',
                  'reservation_time', 'reservation_note', 'guest_number']
        widgets = {
            'reservation_date': forms.DateInput(attrs={'type': 'date'}),
            'reservation_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ReservationForm, self).__init__(*args, **kwargs)
        if self.user:
            self.fields['user'].initial = self.user
            self.fields['user'].widget = forms.HiddenInput()
        self.fields['reservation_date'].widget.attrs.update({'style': 'padding: 0px 0px 0px 25px;'})
        self.fields['guest_number'].widget.attrs.update({'style': 'padding: 0px 0px 0px 25px;'})
        self.fields['email'].widget.attrs.update({'style': 'padding: 0 32px'})

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            phone_number = re.sub(r'\D', '', phone_number)

            if not re.match(r'^0\d{1,9}$', phone_number):
                raise ValidationError(
                    "Please enter a valid phone number starting with 0 and containing up to 10 digits.")

        return phone_number

    def clean_reservation_time(self):
        reservation_date = self.cleaned_data.get('reservation_date')
        reservation_time = self.cleaned_data.get('reservation_time')

        if reservation_date and reservation_time:
            # Convert reservation_time from string to datetime.time
            try:
                reservation_time = datetime.datetime.strptime(reservation_time, '%I:%M %p').time()
                reservation_datetime = timezone.make_aware(
                    datetime.datetime.combine(reservation_date, reservation_time)
                )
                if reservation_datetime <= timezone.now():
                    raise ValidationError("Reservation time must be in the future.")
            except ValueError:
                raise ValidationError("Invalid time format. Please use HH:MM AM/PM format.")

        return reservation_time

    def save(self, commit=True):
        instance = super(ReservationForm, self).save(commit=False)
        if self.user:
            instance.user = self.user
        if commit:
            instance.save()
        return instance
