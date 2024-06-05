from django.db import models

from employee.models import Profile, EmployeeProfile


# Create your models here.
class Vendor(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE)
    user_profile = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='vendor_profile')
    vendor_name = models.CharField(max_length=50)
    vendor_description = models.TextField()
    vendor_license = models.ImageField(upload_to='vendor/license', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name

    class Meta:
        db_table = 'vendor'
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'
