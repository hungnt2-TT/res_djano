# Generated by Django 5.0.6 on 2024-11-09 06:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("menu", "0025_remove_coupon_user"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="coupon",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="coupon",
            name="max_discount",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="coupon",
            name="min_order_value",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
