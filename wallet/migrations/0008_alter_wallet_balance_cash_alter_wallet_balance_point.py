# Generated by Django 5.0.6 on 2024-11-10 17:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("wallet", "0007_alter_subtransaction_amount_cash_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="wallet",
            name="balance_cash",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="wallet",
            name="balance_point",
            field=models.IntegerField(default=0),
        ),
    ]
