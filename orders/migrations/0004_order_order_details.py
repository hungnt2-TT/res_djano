# Generated by Django 5.0.6 on 2024-11-10 13:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0003_order_coupon_id_alter_order_tax_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="order_details",
            field=models.JSONField(default=list),
        ),
    ]
