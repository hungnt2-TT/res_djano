from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.contrib.auth.models import AbstractUser


class Profile(models.Model):
    EMPLOYEE_TYPE_OWNER = 1
    EMPLOYEE_TYPE_CUSTOMER = 2
    EMPLOYEE_TYPE_ADMIN = 3
    EMPLOYEE_TYPE_CANCEL = 4
    EMPLOYEE_TYPE_CHOICES = (
        (EMPLOYEE_TYPE_OWNER, 'owner'),
        (EMPLOYEE_TYPE_CUSTOMER, 'customer'),
        (EMPLOYEE_TYPE_ADMIN, 'admin'),
        (EMPLOYEE_TYPE_CANCEL, 'cancel')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True)
    employee_type = models.IntegerField(choices=EMPLOYEE_TYPE_CHOICES, default=EMPLOYEE_TYPE_OWNER)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


# class Employee(AbstractUser):
#     employee_id = models.CharField(max_length=10, unique=True)
#     department = models.CharField(max_length=50)
#     position = models.CharField(max_length=50)
#     salary = models.DecimalField(max_digits=10, decimal_places=2)
#
#     def __str__(self):
#         return self.username

