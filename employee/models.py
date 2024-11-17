from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, AbstractUser
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.utils.translation import gettext_lazy as _
from django.contrib.gis.db import models as gis_models

from employee.mails import send_mail


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

        user.is_active = True
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
    EMPLOYEE_TYPE_ADMIN = 3
    EMPLOYEE_TYPE_CANCEL = 4
    EMPLOYEE_TYPE_SHIPPER = 5
    EMPLOYEE_TYPE_CHOICES = (
        (EMPLOYEE_TYPE_OWNER, 'owner'),
        (EMPLOYEE_TYPE_CUSTOMER, 'customer'),
        (EMPLOYEE_TYPE_CANCEL, 'cancel'),
        (EMPLOYEE_TYPE_ADMIN, 'admin'),
        (EMPLOYEE_TYPE_SHIPPER, 'shipper'),
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    phone_number_verified = models.BooleanField(default=False)
    employee_type = models.IntegerField(choices=EMPLOYEE_TYPE_CHOICES, default=EMPLOYEE_TYPE_CUSTOMER)
    avatar_shipper = models.ImageField(upload_to='avatar_shipper', blank=True, null=True)
    driving_license = models.ImageField(upload_to='driving_license', blank=True, null=True)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    email_contact = models.CharField(max_length=50, blank=True, null=True, default='email')
    address = models.CharField(max_length=255, blank=True, null=True)
    data_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    verified = models.BooleanField(_("verified"), default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    def get_role(self):
        if self.employee_type == 1:
            user_role = 'owner'
        elif self.employee_type == 2:
            user_role = 'customer'
        elif self.employee_type == 5:
            user_role = 'shipper'
        else:
            user_role = 'admin'
        return user_role

    def is_user(self):
        return self.employee_type == 2

    def send_email_notification(self, order_number, status):
        subject = "Order Status Update"
        message = "Your order has been updated to " + status
        context = {
            'user': self.nickname,
            'message': message,
            'subject': subject,
            'order_number': order_number,
            'status': status
        }
        send_mail(subject, 'mails/notification.html', context)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            old = Profile.objects.get(pk=self.pk)
            if old.is_active != self.is_active and self.employee_type == 5:
                context = {
                    'user': old,
                    'verified': self.is_active
                }

                if self.is_active:
                    mail_sj = 'Congratulation ' + self.username
                    send_mail(mail_sj, 'mails/approved_shipper.html', context)
                else:
                    mail_sj = 'Sorry'
                    send_mail(mail_sj, 'mails/approved_shipper.html', context)
        super(Profile, self).save(*args, **kwargs)

class EmployeeProfile(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='cover_photos', blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    location = gis_models.PointField(geography=True, default=Point(0.0, 0.0), srid=4326)
    address_line_1 = models.CharField(max_length=255, blank=True, null=True)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    address_line_3 = models.CharField(max_length=255, blank=True, null=True)
    success_privacy_policy = models.BooleanField(default=False)
    email_is_confirmed = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.latitude and self.longitude:
            self.location = Point(float(self.longitude), float(self.latitude))
            super(EmployeeProfile, self).save()
        return super(EmployeeProfile, self).save()

    def get_location(self):
        return f'{self.latitude}, {self.longitude}'
class CustomProfile(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    nickname = models.CharField(max_length=50, blank=True, null=True)


class District(models.Model):
    # city_name = models.CharField(max_length=255)
    geom = gis_models.MultiPolygonField(geography=True, srid=4326)
    objectid = models.IntegerField()
    f_code = models.CharField(max_length=255, blank=True, null=True)
    ten_tinh = models.CharField(max_length=255, blank=True, null=True)
    ten_huyen = models.CharField(max_length=255, blank=True, null=True)
    dan_so = models.IntegerField(blank=True, null=True)
    nam_tk = models.IntegerField(blank=True, null=True)
    code_vung = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'districts'
        managed = False

    def __str__(self):
        return self.ten_huyen

    #
    # def get_districts_by_location(self, location):
    #     return self.objects.filter(location=location)
