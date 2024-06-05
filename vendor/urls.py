from django.urls import path
from . import views

urlpatterns = [
    path('register_vendor', views.register_vendor, name='home'),
    ]