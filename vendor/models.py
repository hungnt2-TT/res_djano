from django.db import models

from employee.models import Profile, EmployeeProfile


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
    is_approved = models.BooleanField(default=False)
    address_line_1 = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    pin_code = models.CharField(max_length=10, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)
    location = models.CharField(max_length=50, blank=True, null=True)
    latitude = models.CharField(max_length=50, blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name

    class Meta:
        db_table = 'vendor'
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'
