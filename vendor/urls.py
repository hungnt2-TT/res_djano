from django.urls import path
from . import views

urlpatterns = [
    path('register_vendor', views.register_vendor, name='register_vendor'),
    path('vendor_map', views.vendor_map, name='vendor_map'),
    ]