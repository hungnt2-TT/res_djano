# Generated by Django 5.0.6 on 2024-09-22 10:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("menu", "0009_alter_fooditem_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fooditem",
            name="price",
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]