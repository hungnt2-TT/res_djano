# Generated by Django 5.0.6 on 2024-11-17 16:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("menu", "0028_coupon_vendor"),
    ]

    operations = [
        migrations.AddField(
            model_name="fooditem",
            name="quantity_order",
            field=models.PositiveIntegerField(default=0),
        ),
    ]