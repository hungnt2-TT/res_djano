# Generated by Django 5.0.6 on 2024-11-10 10:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0002_order_coupon_order_subtotal_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="coupon_id",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="order",
            name="tax_data",
            field=models.JSONField(
                blank=True,
                help_text="Data format: {'tax_type':{'tax_percentage':'tax_amount'}}",
                null=True,
            ),
        ),
    ]
