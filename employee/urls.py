from django.urls import path, include
from . import views
from .views import LoginResView, PasswordReset

urlpatterns = [
    path('', views.customer_dashboard),
    path('home/', views.home, name='home'),
    path('history/', views.history, name='history'),
    path('register/', views.register_user, name='register_user'),
    path('register/register_confirm/', views.register_user_confirm, name='register_confirm'),
    path('register/register_save/', views.register_user_save, name='register_save'),
    path('password-reset/', views.PasswordReset.as_view(), name='ep_password_reset'),
    path('password_reset/done/', views.PasswordResetDoneView.as_view(), name='ep_password_reset_done'),
    path('password-reset/complete/', views.PasswordResetComplete.as_view(), name='ep_password_reset_complete'),
    path('password-reset/confirm/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(),
         name='ep_password_reset_confirm'),
    path('password_change/', views.PasswordChange.as_view(), name='p_password_change'),
    path('password_change/done/', views.PasswordChangeDone.as_view(), name='p_password_change_done'),
    path('activate/<slug:uidb64>/<slug:token>/', views.activate, name='activate'),
    path('profile/', views.vendor_profile_update, name='profile'),
    path('middleware_account/', views.middleware_account, name='middleware_account'),
    path('owner/', views.owner_dashboard, name='owner_dashboard'),
    path('customer/', views.customer_dashboard, name='customer_dashboard'),
    path('shipper/', views.shipper_dashboard, name='shipper_dashboard'),

    path('auth-receiver', views.auth_receiver, name='auth_receiver'),
    path('login_by_email/', views.register_by_email, name='login_by_email'),
    path('update_location/', views.update_location, name='update_location'),
    path('send_sms_view/<str:phone_number>/', views.send_sms_view, name='send_sms_view'),
    path('accept-order/<int:order_id>/', views.accept_order, name='accept_order'),
    path('reject-order/<int:order_id>/', views.reject_order, name='reject_order'),

    # shipper
    path('request_ship/', views.request_ship, name='request_ship'),
    path('accept_ship/<int:order_id>/', views.accept_ship, name='accept_ship'),
    path('reject_ship/<int:order_id>/', views.reject_ship, name='reject_ship'),

    # account
    path('delete_account/', views.delete_account, name='delete_account'),

    # favorite
    path('favorites/', views.favorite_list, name='favorite_list'),

]
