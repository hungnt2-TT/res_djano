# Generated by Django 5.0.6 on 2024-10-19 10:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("employee", "0015_alter_profile_employee_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="District",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
            options={"db_table": "districts", "managed": False, },
        ),
    ]
