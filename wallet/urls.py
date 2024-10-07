from django.urls import path
from . import views

urlpatterns = [
    # path('', AccountViews.customer_dashboard),
    path('setting_wallet/', views.setting_wallet, name='setting_wallet'),
    path('daily_check_in/', views.daily_check_in, name='daily_check_in'),
    ]