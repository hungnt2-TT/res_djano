from django.urls import path, include
from . import views

urlpatterns = [
    # path('', AccountViews.customer_dashboard),
    path('', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place-order'),
    path('transaction_order/', views.transaction_order, name='transaction'),
    path('check_phone_verification/', views.check_phone_verification, name='check_phone_verification'),
    path('check_wallet_balance/', views.check_wallet_balance, name='check_wallet_balance'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('order_detail/<str:order_number>/', views.order_detail, name='order_detail'),
]
