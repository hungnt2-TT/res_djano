# Generated by Django 5.0.6 on 2024-11-03 14:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("marketplace", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="cart",
            name="note",
            field=models.TextField(blank=True, null=True),
        ),
    ]