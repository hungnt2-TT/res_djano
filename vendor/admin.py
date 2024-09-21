from django.contrib import admin

# Register your models here.
from .models import Vendor


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('vendor_name', 'vendor_description', 'is_approved', 'create_at', 'updated_at')
    search_fields = ('vendor_name', 'vendor_description')
    list_filter = ('is_approved', 'create_at', 'updated_at')
    date_hierarchy = 'create_at'
    list_editable = ('is_approved',)
