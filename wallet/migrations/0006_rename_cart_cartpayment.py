# Generated by Django 5.0.6 on 2024-10-31 17:14

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("wallet", "0005_rename_updated_at_subtransaction_update_at"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(old_name="Cart", new_name="CartPayment", ),
    ]