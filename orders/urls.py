from django.urls import path, include
from . import views

urlpatterns = [
    # path('', AccountViews.customer_dashboard),
    path('', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place-order'),
    path('transaction/', views.transaction, name='transaction'),
]
