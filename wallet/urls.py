from django.urls import path, include
from . import views

urlpatterns = [
    # path('', AccountViews.customer_dashboard),
    path('setting_wallet/', views.setting_wallet, name='setting_wallet'),
    path('daily_check_in/', views.daily_check_in, name='daily_check_in'),
    path('paypal', include('paypal.standard.ipn.urls')),
    path('payment_success', views.payment_success, name='payment_success'),
    path('payment_failed', views.payment_failed, name='payment_failed'),
    path('payment', views.payment_service_paypal, name='payment_paypal'),
    path('vn_pay', views.payment, name='payment'),
    path('payment_ipn', views.payment_ipn, name='payment_ipn'),
    path('payment_return', views.payment_return, name='payment_return'),
    path('query', views.query, name='query'),
    path('refund', views.refund, name='refund'),
    path('', views.index, name='index'),
]
