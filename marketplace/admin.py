from django.contrib import admin

# Register your models here.
from .models import Cart


class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'food_item', 'quantity', 'is_ordered', 'created_at', 'updated_at']
    list_filter = ['is_ordered', 'created_at', 'updated_at']
    search_fields = ['user', 'food_item', 'quantity']


admin.site.register(Cart, CartAdmin)
