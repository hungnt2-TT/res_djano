# Generated by Django 5.0.6 on 2024-06-14 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0003_vendor_vendor_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='address_line_1',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='city',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='latitude',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='location',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='longitude',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='pin_code',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='state',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]