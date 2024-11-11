# Generated by Django 5.0.6 on 2024-11-06 08:24

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0004_alter_cart_unique_together'),
        ('menu', '0024_remove_coupon_created_by_remove_coupon_food_item_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cart',
            unique_together={('food_item', 'size', 'user')},
        ),
    ]
