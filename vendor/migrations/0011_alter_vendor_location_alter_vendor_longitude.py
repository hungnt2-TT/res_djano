# Generated by Django 5.0.6 on 2024-06-26 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0010_alter_vendor_longitude'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='location',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='longitude',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
