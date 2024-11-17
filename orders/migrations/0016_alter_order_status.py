# Generated by Django 5.0.6 on 2024-11-15 14:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0015_merge_20241115_0557"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("New Order", "New Order"),
                    ("Processing Payment", "Processing Payment"),
                    ("Payment Failed", "Payment Failed"),
                    ("Payment Completed", "Payment Completed"),
                    ("Waiting for Confirmation", "Waiting for Confirmation"),
                    ("Accepted", "Accepted"),
                    ("Shipper Assigned", "Shipper Assigned"),
                    ("Completed", "Completed"),
                    ("Cancelled", "Cancelled"),
                    ("In Transit", "In Transit"),
                    ("Delivered", "Delivered"),
                ],
                default="New",
                max_length=24,
            ),
        ),
    ]
