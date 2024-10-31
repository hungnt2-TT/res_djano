from django.contrib import admin

from orders.models import Order, OrderedFood

# Register your models here.
admin.site.register(Order)
admin.site.register(OrderedFood)
