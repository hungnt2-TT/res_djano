# Generated by Django 5.0.6 on 2024-06-20 04:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0004_vendor_address_line_1_vendor_city_vendor_latitude_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='cover_photo',
            field=models.ImageField(blank=True, null=True, upload_to='vendor/cover_photo'),
        ),
    ]
