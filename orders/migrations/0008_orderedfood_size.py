# Generated by Django 5.0.6 on 2024-11-10 17:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0007_orderedfood_note"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderedfood",
            name="size",
            field=models.CharField(default=26, max_length=50),
            preserve_default=False,
        ),
    ]