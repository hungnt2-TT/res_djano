from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Profile, EmployeeProfile


@receiver(post_save, sender=Profile)
def create_employee_profile(sender, instance, created, **kwargs):
    if created:
        EmployeeProfile.objects.create(user=instance)
    else:
        try:
            profile = EmployeeProfile.objects.get(user=instance)
            profile.save()
        except:
            EmployeeProfile.objects.create(user=instance)


@receiver(pre_save, sender=Profile)
def pre_save_employee_profile(sender, instance, **kwargs):
    print("pre_save_employee_profile")
