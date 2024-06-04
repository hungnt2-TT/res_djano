from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('register/', views.register_user, name='register'),
    path('register/register_confirm/', views.register_user_confirm, name='register_confirm'),
    path('register/register_save/', views.register_user_save, name='register_save')
    ]