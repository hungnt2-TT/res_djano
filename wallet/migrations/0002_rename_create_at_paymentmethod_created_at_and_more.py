# Generated by Django 5.0.6 on 2024-10-01 04:32

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paymentmethod',
            old_name='create_at',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='subtransaction',
            old_name='amount',
            new_name='amount_cash',
        ),
        migrations.RenameField(
            model_name='subtransaction',
            old_name='transaction',
            new_name='transaction_id',
        ),
        migrations.RenameField(
            model_name='transaction',
            old_name='receiver',
            new_name='user_id_from',
        ),
        migrations.RenameField(
            model_name='transaction',
            old_name='creator',
            new_name='user_id_to',
        ),
        migrations.RenameField(
            model_name='wallet',
            old_name='payment_method',
            new_name='currency_id',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='account_name',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='account_number',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='bank',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='cvv',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='expiry_date',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='id',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='payment_method',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='paypal_email',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='user',
        ),
        migrations.RemoveField(
            model_name='subtransaction',
            name='transaction_type',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='payment_method',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='running_balance',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='value',
        ),
        migrations.RemoveField(
            model_name='wallet',
            name='balance',
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='description'),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='method',
            field=models.IntegerField(choices=[(0, 'Unknown'), (1, 'Bank Transfer'), (2, 'Wallet'), (3, 'Paypal'), (4, 'Cash')], default=0),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='name',
            field=models.CharField(default=2022, max_length=100, verbose_name='name'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AddField(
            model_name='subtransaction',
            name='amount_point',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='subtransaction',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('completed', 'completed'), ('rejected', 'rejected')], default='pending', max_length=50),
        ),
        migrations.AddField(
            model_name='subtransaction',
            name='wallet_id_from',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to='wallet.wallet'),
        ),
        migrations.AddField(
            model_name='subtransaction',
            name='wallet_id_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='creator', to='wallet.wallet'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('completed', 'completed'), ('rejected', 'rejected')], default='pending', max_length=50),
        ),
        migrations.AddField(
            model_name='wallet',
            name='balance_cash',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='wallet',
            name='balance_point',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='wallet',
            name='description',
            field=models.TextField(default=2023),
            preserve_default=False,
        ),
    ]