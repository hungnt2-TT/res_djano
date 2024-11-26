# Generated by Django 5.0.6 on 2024-11-24 13:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("menu", "0029_fooditem_quantity_order"),
    ]

    operations = [
        migrations.RemoveField(model_name="fooditem", name="time_range", ),
        migrations.AddField(
            model_name="category",
            name="time_range",
            field=models.CharField(
                choices=[
                    ("morning", "6:00-12:00"),
                    ("afternoon", "12:00-18:00"),
                    ("evening", "18:00-24:00"),
                    ("night", "0:00-6:00"),
                    ("all_day", "00:01-23:59"),
                ],
                default="morning",
                max_length=10,
            ),
        ),
    ]