# Generated by Django 5.0.6 on 2024-11-03 13:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("menu", "0020_alter_fooditem_discounted_price_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fooditem",
            name="old_price",
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name="fooditem",
            name="price",
            field=models.IntegerField(default=0, null=True),
        ),
    ]
