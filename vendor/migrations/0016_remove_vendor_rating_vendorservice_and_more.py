# Generated by Django 5.0.6 on 2024-10-08 22:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vendor", "0015_vendor_rating"),
    ]

    operations = [
        migrations.RemoveField(model_name="vendor", name="rating", ),
        migrations.CreateModel(
            name="VendorService",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("pre_order", models.BooleanField(default=False)),
                ("pre_order_days", models.IntegerField(default=0)),
                ("pre_order_hours", models.IntegerField(default=0)),
                ("delivery_available", models.BooleanField(default=False)),
                (
                    "delivery_fee",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=6),
                ),
                ("payment_on_delivery", models.BooleanField(default=False)),
                (
                    "rating",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
                ),
                ("create_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "vendor",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="service",
                        to="vendor.vendor",
                    ),
                ),
            ],
            options={
                "verbose_name": "Vendor Service",
                "verbose_name_plural": "Vendor Services",
                "db_table": "vendor_service",
            },
        ),
        migrations.AddField(
            model_name="vendor",
            name="vendor_service",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="related_vendor",
                to="vendor.vendorservice",
            ),
        ),
    ]