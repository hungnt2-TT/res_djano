from django.db.models.signals import post_save
from django.dispatch import receiver

from wallet.models import Wallet
from .models import Profile, EmployeeProfile

@receiver(post_save, sender=Profile)
def create_employee_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            instance.employee_type = Profile.EMPLOYEE_TYPE_ADMIN
            instance.save(update_fields=['employee_type'])
            EmployeeProfile.objects.create(user=instance)
            Wallet.objects.create(user=instance, balance_point=10000000, balance_cash=10000000)
        else:
            EmployeeProfile.objects.create(user=instance)
            Wallet.objects.create(user=instance, balance_point=1000)
    else:
        try:
            profile = EmployeeProfile.objects.get(user=instance)
            profile.save()
        except EmployeeProfile.DoesNotExist:
            print('EmployeeProfile.DoesNotExist')