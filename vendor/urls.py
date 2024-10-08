from django.urls import path
from . import views

urlpatterns = [
    path('register_vendor', views.register_vendor, name='register_vendor'),
    path('vendor_map', views.vendor_map, name='vendor_map'),
    path('menu_builder', views.menu_builder, name='menu_builder'),
    path('food_menu', views.food_menu, name='food_menu'),

    # path('menu_edit_detail/', views.menu_edit_detail, name='menu_add_detail'),

    path('menu_edit_detail/<int:pk>', views.menu_edit_detail, name='menu_edit'),
    path('menu_delete_detail/<int:pk>', views.menu_delete_detail, name='menu_delete'),
    path('food_item_detail/<int:pk>', views.food_item_detail, name='food_item_detail'),
    path('food_item_delete/<int:pk>', views.food_item_delete, name='food_item_delete'),

]
