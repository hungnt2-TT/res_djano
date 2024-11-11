# Generated by Django 5.0.6 on 2024-11-06 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0023_alter_size_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coupon',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='coupon',
            name='food_item',
        ),
        migrations.RemoveField(
            model_name='coupon',
            name='wallet',
        ),
        migrations.AddField(
            model_name='coupon',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
