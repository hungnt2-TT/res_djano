from django.contrib import admin
from .models import Profile, EmployeeProfile
from django.contrib.auth.admin import UserAdmin


# Register your models here.

class CustomUserAdmin(UserAdmin):
    list_display = ['id', 'first_name', 'last_name', 'username', 'email', 'phone_number', 'employee_type', 'nickname']
    ordering = ('-data_joined',)
    filter_horizontal = []  # Update this
    list_filter = []  # And this
    fieldsets = ()


admin.site.register(Profile, CustomUserAdmin)
admin.site.register(EmployeeProfile)