# Generated by Django 5.0.6 on 2024-10-06 04:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("employee", "0013_employeeprofile_city_employeeprofile_latitude_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="phone_number_verified",
            field=models.BooleanField(default=False),
        ),
    ]
