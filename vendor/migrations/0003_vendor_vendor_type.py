# Generated by Django 5.0.6 on 2024-06-11 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0002_vendor_fax_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='vendor_type',
            field=models.IntegerField(choices=[(0, 'unknown'), (1, 'free'), (2, 'premium'), (3, 'standard')], default=0),
        ),
    ]