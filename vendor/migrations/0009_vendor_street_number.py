# Generated by Django 5.0.6 on 2024-06-26 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0008_remove_vendor_information'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='street_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
