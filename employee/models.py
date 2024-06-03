from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, username, email, password=None):
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=self.normalize_email(email),
            password=password,
        )
        user.is_admin = True
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class Profile(AbstractBaseUser):
    EMPLOYEE_TYPE_OWNER = 1
    EMPLOYEE_TYPE_CUSTOMER = 2
    EMPLOYEE_TYPE_CANCEL = 4
    EMPLOYEE_TYPE_CHOICES = (
        (EMPLOYEE_TYPE_OWNER, 'owner'),
        (EMPLOYEE_TYPE_CUSTOMER, 'customer'),
        (EMPLOYEE_TYPE_CANCEL, 'cancel')
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    employee_type = models.IntegerField(choices=EMPLOYEE_TYPE_CHOICES, default=EMPLOYEE_TYPE_OWNER)
    nickname = models.CharField(max_length=50, blank=True, null=True)

    data_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class EmployeeProfile(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='cover_photos', blank=True, null=True)
    address_line_1 = models.CharField(max_length=50, blank=True, null=True)
    address_line_2 = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    pin_code = models.CharField(max_length=10, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)
    latitude = models.CharField(max_length=50, blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email
