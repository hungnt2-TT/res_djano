from django.urls import path
from employee import views as AccountViews
from . import views

urlpatterns = [
    path('', AccountViews.customer_dashboard),
    path('setting/', views.cprofile, name='cprofile'),
    path('customer_setting/', views.customer_setting, name='customer_setting'),
    path('order_ship/', views.order_ship, name='order_ship'),
    path('start_ship/', views.start_ship, name='start_ship'),
    path('complated_ship/', views.complated_ship, name='complated_ship'),
    ]