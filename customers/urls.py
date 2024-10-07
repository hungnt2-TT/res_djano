from django.urls import path
from employee import views as AccountViews
from . import views

urlpatterns = [
    path('', AccountViews.customer_dashboard),
    path('setting/', views.cprofile, name='cprofile'),
    path('customer_setting/', views.customer_setting, name='customer_setting'),
    ]