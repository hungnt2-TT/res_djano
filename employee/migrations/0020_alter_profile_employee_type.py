# Generated by Django 5.0.6 on 2024-11-11 14:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("employee", "0019_employeeprofile_state"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="employee_type",
            field=models.IntegerField(
                choices=[
                    (1, "owner"),
                    (2, "customer"),
                    (4, "cancel"),
                    (3, "admin"),
                    (5, "shipper"),
                ],
                default=2,
            ),
        ),
    ]
