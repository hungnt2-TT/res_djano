# Generated by Django 5.0.6 on 2024-11-03 07:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("menu", "0018_alter_fooditem_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="fooditem",
            name="food_title",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="fooditem",
            name="sub_food_title",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]