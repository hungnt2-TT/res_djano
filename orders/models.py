from django.db import models

from employee.models import Profile
from menu.models import FoodItem
from vendor.models import Vendor
from wallet.models import PaymentMethod


# Create your models here.
class Order(models.Model):
    STATUS = (
        ('New Order', 'New Order'),
        ('Processing Payment', 'Processing Payment'),
        ('Payment Failed', 'Payment Failed'),
        ('Payment Completed', 'Payment Completed'),
        ('Waiting for Confirmation', 'Waiting for Confirmation'),

        ('Accepted', 'Accepted'),
        ('Shipper Pending', 'Shipper Pending'),
        ('Shipper Assigned', 'Shipper Assigned'),
        ('Shipper Rejected', 'Shipper Rejected'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('In Transit', 'In Transit'),
        ('Delivered', 'Delivered'),
    )
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    vendors = models.ManyToManyField(Vendor)
    payment = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    shipper = models.ForeignKey(Profile, null=True, blank=True, on_delete=models.SET_NULL, related_name='orders')
    assigned_at = models.DateTimeField(null=True, blank=True)

    order_number = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address = models.CharField(max_length=250)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    pin_code = models.CharField(max_length=10)
    subtotal = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    order_details = models.JSONField(default=list)
    delivery_status = models.CharField(max_length=20,
                                       choices=[('In Transit', 'In Transit'), ('Delivered', 'Delivered')], null=True,
                                       blank=True)
    tax_data = models.JSONField(blank=True, help_text="Data format: {'tax_type':{'tax_percentage':'tax_amount'}}",
                                null=True)
    is_payment_completed = models.BooleanField(default=False)
    total_tax = models.IntegerField(default=0)
    total_shipping_cost = models.IntegerField(default=0)
    total_delivery_time = models.IntegerField(default=0)
    coupon = models.CharField(max_length=50, blank=True, null=True)
    coupon_id = models.IntegerField(blank=True, null=True)
    payment_method = models.CharField(max_length=100)
    status = models.CharField(max_length=24, choices=STATUS, default='New')
    is_ordered = models.BooleanField(default=False)
    message_error = models.TextField(null=True, blank=True)
    attempts = models.IntegerField(default=0)
    proof_image = models.ImageField(upload_to='order/proof', blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def order_total(self):
        return self.total + self.total_tax

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'

    def check_delivery_status(self):

        if self.status == 'Completed':
            return 'Delivered'
        elif self.status == 'Accepted':
            return 'In Transit'
        elif self.status == 'Waiting for Confirmation':
            return 'Waiting for Confirmation'
        elif self.status == 'Delivering':
            return 'Delivering'
        else:
            return None
    def __str__(self):
        return self.order_number

    def get_vendor_by_order_details(self):
        if self.order_details:
            return self.order_details[0]['vendor']
        return None


class OrderedFood(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    size = models.CharField(max_length=50)
    fooditem = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField(default=0)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fooditem