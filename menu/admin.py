from django.contrib import admin

from menu.models import Category, FoodItem, Coupon


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name', 'vendor', 'created_at', 'updated_at', ]
    search_fields = ['category_name']
    prepopulated_fields = {'slug': ('category_name',)}


class FoodItemAdmin(admin.ModelAdmin):
    list_display = ['food_name', 'category', 'price', 'is_available', 'created_at', 'updated_at']
    search_fields = ['food_name']
    prepopulated_fields = {'slug': ('food_name',)}


class CouponAdmin(admin.ModelAdmin):
    list_display = ['coupon_code', 'description', 'min_order_value', 'max_discount', 'usage_limit', 'created_by', 'current_usage']
    search_fields = ['coupon_code']


# Register your models here.
admin.site.register(Category, CategoryAdmin)
admin.site.register(FoodItem)
admin.site.register(Coupon, CouponAdmin)
