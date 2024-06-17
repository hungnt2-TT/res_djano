from django.urls import path, include
from . import views
from .views import LoginResView, PasswordReset

urlpatterns = [
    path('home/', views.home, name='home'),
    path('register/', views.register_user, name='register_user'),
    path('register/register_confirm/', views.register_user_confirm, name='register_confirm'),
    path('register/register_save/', views.register_user_save, name='register_save'),
    path('password-reset/', views.PasswordReset.as_view(), name='ep_password_reset'),
    path('password_reset/done/', views.PasswordResetDoneView.as_view(), name='ep_password_reset_done'),
    path('password-reset/complete/', views.PasswordResetComplete.as_view(), name='ep_password_reset_complete'),
    path('password-reset/confirm/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name='ep_password_reset_confirm'),


]
