# Generated by Django 5.0.6 on 2024-10-20 16:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vendor", "0017_vendorservice_booking"),
    ]

    operations = [
        migrations.AddField(
            model_name="vendor",
            name="name_district",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
