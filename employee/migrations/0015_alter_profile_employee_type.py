# Generated by Django 5.0.6 on 2024-10-06 07:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("employee", "0014_profile_phone_number_verified"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="employee_type",
            field=models.IntegerField(
                choices=[(1, "owner"), (2, "customer"), (4, "cancel")], default=2
            ),
        ),
    ]
