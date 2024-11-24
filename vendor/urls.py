from django.urls import path
from . import views

urlpatterns = [
    path('register_vendor', views.register_vendor, name='register_vendor'),
    path('register_shipper', views.register_shipper, name='register_shipper'),
    path('vendor_map', views.vendor_map, name='vendor_map'),
    path('menu_builder', views.menu_builder, name='menu_builder'),
    path('food_menu', views.food_menu, name='food_menu'),

    # path('menu_edit_detail/', views.menu_edit_detail, name='menu_add_detail'),

    path('menu_edit_detail/<int:pk>', views.menu_edit_detail, name='menu_edit'),
    path('menu_delete_detail/<int:pk>', views.menu_delete_detail, name='menu_delete'),
    path('food_item_detail/<int:pk>', views.food_item_detail, name='food_item_detail'),
    path('food_item_delete/<int:pk>', views.food_item_delete, name='food_item_delete'),

    path('order_detail/<str:order_number>/', views.order_detail, name='vendor_order_detail'),
    path('my_orders/', views.my_orders, name='vendor_my_orders'),

    path('request_orders/', views.request_orders, name='request_orders'),

    # toggle_favorite
    path('toggle-favorite/<int:vendor_id>/', views.toggle_favorite, name='toggle_favorite'),

    # opening hours
    path('opening_hours/', views.opening_hours, name='opening_hours'),
    path('opening_hours_add/', views.opening_hours_add, name='opening_hours_add'),
    path('opening_hours_edit/<int:pk>', views.opening_hours_edit, name='opening_hours_edit'),
    path('opening_hours_delete/<int:pk>', views.opening_hours_delete, name='opening_hours_delete'),
]
