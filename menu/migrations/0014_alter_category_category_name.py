# Generated by Django 5.0.6 on 2024-11-01 15:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("menu", "0013_fooditem_discounted_price_fooditem_old_price_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="category_name",
            field=models.CharField(max_length=50),
        ),
    ]
