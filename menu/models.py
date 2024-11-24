import uuid
import random
import string
from decimal import Decimal
from imp import reload
import joblib
import os
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from django.db import models

from employee.models import Profile
from vendor.models import Vendor
from wallet.models import Wallet

from django.template.defaultfilters import slugify
from django_ckeditor_5.fields import CKEditor5Field


#
# model_path = os.path.join(settings.BASE_DIR, 'menu', 'food_time_model.pkl')
# vectorizer_path = os.path.join(settings.BASE_DIR, 'menu', 'vectorizer.pkl')
#
# clf = joblib.load(model_path)
# vectorizer = joblib.load(vectorizer_path)


# Create your models here.
class Category(models.Model):
    TIME_RANGES = [
        ('morning', '6:00-12:00'),
        ('afternoon', '12:00-18:00'),
        ('evening', '18:00-24:00'),
        ('night', '0:00-6:00'),
        ('all_day', '00:01-23:59')
    ]
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)
    description = CKEditor5Field(null=True, blank=True, config_name='default')
    time_range = models.CharField(max_length=10, choices=TIME_RANGES, default='morning')
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
        model_path = os.path.join(settings.BASE_DIR, 'menu', 'food_time_model.pkl')
        vectorizer_path = os.path.join(settings.BASE_DIR, 'menu', 'vectorizer.pkl')

        print('model_path', model_path)
        print('vectorizer_path', vectorizer_path)
        # Kiểm tra nếu model và vectorizer tồn tại
        if os.path.exists(model_path) and os.path.exists(vectorizer_path):
            # Tải mô hình và vectorizer
            clf = joblib.load(model_path)
            vectorizer = joblib.load(vectorizer_path)
            print('clf', clf)
            # Kiểm tra nếu time_range chưa được xác định, tiến hành dự đoán
            print('self.food_name', self.category_name)
            food_name_lower = self.category_name.lower()
            # Chuyển tên món ăn thành vector
            test_category = vectorizer.transform([food_name_lower])
            print('test_food', test_category)
            # Dự đoán time_range và gán vào thuộc tính của đối tượng
            print('clf.predict(test_food)', clf.predict(test_category))
            self.time_range = clf.predict(test_category)[0]
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
    image = models.ImageField(upload_to='food_items/')
    is_available = models.BooleanField(default=True)
    quantity_order = models.PositiveIntegerField(default=0)
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

    coupon_code = models.CharField(max_length=50, unique=True, blank=True)
    description = CKEditor5Field('Description', config_name='extends')
    coupon_creation_date = models.DateTimeField(auto_now_add=True)
    coupon_expiry_date = models.DateTimeField()
    redeemed = models.BooleanField(default=False)
    redeemed_at = models.DateTimeField(null=True, blank=True)
    discount_value = models.IntegerField()
    type_of_discount = models.CharField(max_length=50, choices=TYPE_OF_DISCOUNT_CHOICES, default=PERCENTAGE)
    min_order_value = models.IntegerField(null=True, blank=True)
    max_discount = models.IntegerField(null=True, blank=True)
    usage_limit = models.IntegerField(default=1)
    current_usage = models.IntegerField(default=0)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.coupon_code

    def is_valid(self):
        from django.utils import timezone

        if self.coupon_expiry_date < timezone.now():
            print("Coupon expired:", self.coupon_expiry_date)
            return False

        if self.usage_limit and self.current_usage >= self.usage_limit:
            self.redeemed = True
            self.save()
            print("Coupon usage limit reached. Current usage:", self.current_usage, "Limit:", self.usage_limit)
            return False

        print("Coupon is valid.")
        return True

    def apply_discount(self, order_total, delivery_fee=0):

        if not self.is_valid() or (self.min_order_value and order_total < self.min_order_value):
            return order_total

        order_total = order_total
        discount_value = self.discount_value
        discount = 0
        if self.type_of_discount == self.PERCENTAGE:
            discount = discount_value * order_total / 100
        elif self.type_of_discount == self.FREE_DELIVERY:
            discount = min(delivery_fee, self.max_discount if self.max_discount else delivery_fee)
        elif self.type_of_discount == self.REFUND_COIN:
            return {'refund_coin': discount_value, 'discount': 0}
        if self.max_discount:
            discount = min(discount, float(self.max_discount))
        return {'discount': discount, 'refund_coin': 0}

    def successfully_redeemed(self, user):
        from django.utils import timezone
        if self.user is not None:
            if self.redeemed:
                return False
            self.redeemed = True
            self.redeemed_at = timezone.now()
        self.current_usage += 1
        if self.usage_limit is not None:
            self.usage_limit -= 1
        if self.user is not None:
            self.user = user
        self.save()
        return self

    def save(self, *args, **kwargs):
        if self.min_order_value is None or self.min_order_value < 0:
            self.min_order_value = 0
        if not self.coupon_code:
            self.coupon_code = self.generate_coupon_code()

        if not self.coupon_code:
            self.coupon_code = generate_coupon_code()

        super(Coupon, self).save(*args, **kwargs)

    @staticmethod
    def generate_coupon_code(length=8):
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choices(characters, k=length))
