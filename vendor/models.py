from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

from employee.mails import send_mail
from employee.models import Profile, EmployeeProfile, District

from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from datetime import time, date, datetime


class VendorService(models.Model):
    vendor = models.OneToOneField('Vendor', on_delete=models.CASCADE, related_name='service')
    pre_order = models.BooleanField(default=False)
    pre_order_days = models.IntegerField(default=0)
    pre_order_hours = models.IntegerField(default=0)
    delivery_available = models.BooleanField(default=False)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    payment_on_delivery = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    booking = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vendor_service'
        verbose_name = 'Vendor Service'
        verbose_name_plural = 'Vendor Services'

    def __str__(self):
        return f"Services for {self.vendor.vendor_name}"


# Create your models here.
class Vendor(models.Model):
    VENDOR_TYPE_UNKNOWN = 0
    VENDOR_TYPE_FREE = 1
    VENDOR_TYPE_PREMIUM = 2
    VENDOR_TYPE_STANDARD = 3
    VENDOR_TYPE_CHOICES = (
        (VENDOR_TYPE_UNKNOWN, 'unknown'),
        (VENDOR_TYPE_FREE, 'free'),
        (VENDOR_TYPE_PREMIUM, 'premium'),
        (VENDOR_TYPE_STANDARD, 'standard')
    )
    user = models.OneToOneField(Profile, on_delete=models.CASCADE)
    user_profile = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='vendor_profile')
    fax_number = models.CharField(max_length=15, blank=True, null=True)
    vendor_name = models.CharField(max_length=50)
    vendor_type = models.IntegerField(choices=VENDOR_TYPE_CHOICES, default=VENDOR_TYPE_UNKNOWN)
    vendor_description = models.TextField()
    vendor_license = models.ImageField(upload_to='vendor/license', blank=True, null=True)
    vendor_id_card = models.ImageField(upload_to='vendor/id_card', blank=True, null=True)
    vendor_tax_code = models.CharField(max_length=50, blank=True, null=True)
    vendor_slug = models.SlugField(max_length=50, blank=True, null=True, unique=True)
    is_approved = models.BooleanField(default=False)
    street_number = models.CharField(max_length=50, blank=True, null=True)
    address_line_1 = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    pin_code = models.CharField(max_length=10, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)
    location = gis_models.PointField(geography=True, default=Point(0.0, 0.0), srid=4326)
    latitude = models.CharField(max_length=50, blank=True, null=True)
    name_district = models.CharField(max_length=255, blank=True, null=True)
    # pre_order = models.BooleanField(default=False)
    # pre_order_days = models.IntegerField(default=0)
    # pre_order_hours = models.IntegerField(default=0)
    vendor_service = models.OneToOneField(VendorService, on_delete=models.CASCADE, null=True, blank=True,
                                          related_name='related_vendor')
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name

    def save(self, *args, **kwargs):
        self.vendor_name = self.vendor_name.upper()
        self.vendor_slug = slugify(self.vendor_name) + '-' + str(self.user.id)
        if self.pk is not None:
            old = Vendor.objects.get(pk=self.pk)
            if old.is_approved != self.is_approved:
                context = {
                    'vendor': old,
                    'approved': self.is_approved,
                    'user': self.user
                }
                print('Vendor is approved:', self.is_approved)
                if self.is_approved:
                    mail_sj = 'Congratulation ' + self.vendor_name
                    send_mail(mail_sj, 'mails/approved.html', context)
                else:
                    mail_sj = 'Sorry'
                    send_mail(mail_sj, 'mails/approved.html', context)

        if self.longitude and self.latitude:
            self.location = Point(float(self.longitude), float(self.latitude), srid=4326)
            self.name_district = District.objects.get(geom__contains=self.location).ten_huyen
        return super(Vendor, self).save(*args, **kwargs)

    def vendor_id(self):
        return self.id

    class Meta:
        db_table = 'vendor'
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'


class Reservation(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=255, blank=True, null=True)
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    reservation_status = models.BooleanField(default=False)
    reservation_note = models.TextField(blank=True, null=True)
    guest_number = models.IntegerField(default=1)
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reservation'
        verbose_name = 'Reservation'
        verbose_name_plural = 'Reservations'

    def __str__(self):
        return f"Reservation for {self.vendor.vendor_name} by {self.user.user.username}"


DAYS = [
    (1, ("Monday")),
    (2, ("Tuesday")),
    (3, ("Wednesday")),
    (4, ("Thursday")),
    (5, ("Friday")),
    (6, ("Saturday")),
    (7, ("Sunday")),
]

HOUR_OF_DAY_24 = [(time(h, m).strftime('%I:%M %p'), time(h, m).strftime('%I:%M %p')) for h in range(0, 24) for m in
                  (0, 30)]


class OpeningHour(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True)
    to_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('day', '-from_hour')
        unique_together = ('vendor', 'day', 'from_hour', 'to_hour')

    def __str__(self):
        return self.get_day_display()
