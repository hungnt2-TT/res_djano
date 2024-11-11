from django.urls import path, include
from . import views
from .views import convert_to_words

urlpatterns = [
    path('', views.marketplace, name='marketplace'),
    path('maketplace/<slug:vendor_slug>/', views.vendor_detail, name='vendor_detail'),
    path('add_to_cart/<int:food_item_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:food_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.cart, name='cart_store'),
    path('delete_cart_item/<int:cart_id>/', views.delete_cart_item, name='delete_cart_item'),
    path('cart/convert-to-words/', convert_to_words, name='convert_to_words'),
    path('food_item/<int:id>/', views.food_item_detail, name='food_item_detail'),
    path('reservation_booking/', views.reservation_booking, name='reservation_booking'),
    path('search/', views.search, name='search'),
]
