# Generated by Django 5.0.6 on 2024-11-01 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0018_vendor_name_district'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='vendor_id_card',
            field=models.ImageField(blank=True, null=True, upload_to='vendor/id_card'),
        ),
        migrations.AddField(
            model_name='vendor',
            name='vendor_tax_code',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
