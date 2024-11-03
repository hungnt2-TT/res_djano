import uuid
import random
import string
from decimal import Decimal
from imp import reload
import joblib
import os
from django.conf import settings
from django.core.exceptions import ValidationError

from django.db import models

from employee.models import Profile
from vendor.models import Vendor
from wallet.models import Wallet

from django.template.defaultfilters import slugify
from django_ckeditor_5.fields import CKEditor5Field

model_path = os.path.join(settings.BASE_DIR, 'menu', 'food_time_model.pkl')
vectorizer_path = os.path.join(settings.BASE_DIR, 'menu', 'vectorizer.pkl')

clf = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)


# Create your models here.
class Category(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)
    description = CKEditor5Field(null=True, blank=True, config_name='default')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.category_name

    def save(
            self, *args, **kwargs
    ):
        self.slug = slugify(self.category_name) + '-' + str(self.id)
        super(Category, self).save(*args, **kwargs)


class Size(models.Model):
    SIZE_CHOICES = [
        ('N', 'Normal'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Extra Extra Large'),
    ]
    size = models.CharField(max_length=3, choices=SIZE_CHOICES)
    price = models.IntegerField(default=0)
    food_item = models.ForeignKey('FoodItem', related_name='size_items', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.get_size_display()} - {self.price} VND"

class FoodItem(models.Model):
    TIME_RANGES = [
        ('morning', '6:00-12:00'),
        ('afternoon', '12:00-18:00'),
        ('evening', '18:00-24:00'),
        ('night', '0:00-6:00'),
    ]
    sizes = models.ManyToManyField(Size, related_name="food_items")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendor_food_items')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='food_items')
    food_name = models.CharField(max_length=50)
    food_title = models.CharField(max_length=255, null=True, blank=True)
    sub_food_title = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(max_length=50)
    description = CKEditor5Field('Description', config_name='extends')
    price = models.IntegerField(null=True, default=0)
    old_price = models.IntegerField(null=True, default=0)
    discounted_price = models.IntegerField(null=True, default=0)
    sale_end_time = models.DateTimeField(null=True, blank=True)
    time_range = models.CharField(max_length=10, choices=TIME_RANGES, default='morning')
    image = models.ImageField(upload_to='food_items/')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.food_name

    def save(
            self, *args, **kwargs
    ):
        self.slug = slugify(self.food_name)
        if self.price < 0 or None:
            self.price = 0
        if not self.time_range:
            test_food = vectorizer.transform([self.name])
            self.time_range = clf.predict(test_food)[0]
        super(FoodItem, self).save(*args, **kwargs)


def generate_coupon_code(length=15):
    """Generate a random coupon code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


class Coupon(models.Model):
    FREE_DELIVERY = 'Free Delivery'
    PERCENTAGE = 'Percentage'
    REFUND_COIN = 'Refund Coin'
    TYPE_OF_DISCOUNT_CHOICES = [
        (FREE_DELIVERY, 'Free Delivery'),
        (PERCENTAGE, 'Percentage'),
        (REFUND_COIN, 'Refund Coin')
    ]
    CREATED_BY_VENDOR = 'Vendor'
    CREATED_BY_ADMIN = 'Admin'
    CREATED_BY_CHOICES = [
        (CREATED_BY_VENDOR, 'Vendor'),
        (CREATED_BY_ADMIN, 'Admin')
    ]
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    coupon_code = models.CharField(max_length=50, unique=True, blank=True)
    description = CKEditor5Field('Description', config_name='extends')
    coupon_creation_date = models.DateTimeField(auto_now_add=True)
    coupon_expiry_date = models.DateTimeField()
    redeemed = models.BooleanField(default=False)
    redeemed_at = models.DateTimeField(null=True, blank=True)
    discount_value = models.DecimalField(max_digits=5, decimal_places=2)
    type_of_discount = models.CharField(max_length=50, choices=TYPE_OF_DISCOUNT_CHOICES, default=PERCENTAGE)
    min_order_value = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    usage_limit = models.IntegerField(default=1)
    current_usage = models.IntegerField(default=0)
    created_by = models.CharField(max_length=10, choices=CREATED_BY_CHOICES, default='admin')

    def __str__(self):
        return self.coupon_code

    def is_valid(self):
        from django.utils import timezone
        return self.coupon_expiry_date >= timezone.now() and (
                not self.usage_limit or self.current_usage < self.usage_limit)

    def apply_discount(self, order_total):
        if not self.is_valid():
            return order_total

        discount = 0
        if self.type_of_discount == self.PERCENTAGE:
            discount = self.discount_value * order_total / 100
        elif self.type_of_discount in [self.REFUND_COIN, self.FREE_DELIVERY]:
            discount = self.discount_value

        if self.max_discount:
            discount = min(discount, self.max_discount)

        return discount

    def successfully_redeemed(self):
        from django.utils import timezone
        self.current_usage += 1
        self.redeemed = True
        self.redeemed_at = timezone.now()
        self.save()

    def save(self, *args, **kwargs):
        if self.min_order_value is None or self.min_order_value < 0:
            self.min_order_value = 0

        if self.created_by == self.CREATED_BY_VENDOR:
            if not self.user.get_role() == 'owner':
                raise PermissionError("Only vendors can create coupons for their own products.")
            if self.food_item.vendor != self.user.vendor:
                raise PermissionError("Vendors can only create coupons for their own products.")
        elif self.created_by == self.CREATED_BY_ADMIN:
            if not self.user.is_admin:
                raise PermissionError("Only admins can create coupons for all products.")

        if not self.coupon_code:
            self.coupon_code = generate_coupon_code()

        super(Coupon, self).save(*args, **kwargs)
