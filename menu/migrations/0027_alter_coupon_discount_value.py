# Generated by Django 5.0.6 on 2024-11-09 13:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("menu", "0026_coupon_user_alter_coupon_max_discount_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="coupon", name="discount_value", field=models.IntegerField(),
        ),
    ]
