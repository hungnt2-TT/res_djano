from datetime import timezone

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from employee.models import Profile
import uuid
from django.urls import reverse


# CURRENCY_STORE_FIELD = getattr(settings,
#                                'WALLET_CURRENCY_STORE_FIELD', models.BigIntegerField)


class PaymentMethod(models.Model):
    PAYMENT_METHOD_UNKNOWN = 0
    PAYMENT_METHOD_BANK_TRANSFER = 1
    PAYMENT_METHOD_WALLET = 2
    PAYMENT_METHOD_PAYPAL = 3
    PAYMENT_METHOD_CASH = 4
    PAYMENT_METHOD_CHOICES = (
        (PAYMENT_METHOD_UNKNOWN, _('Unknown')),
        (PAYMENT_METHOD_BANK_TRANSFER, _('Bank Transfer')),
        (PAYMENT_METHOD_WALLET, _('Wallet')),
        (PAYMENT_METHOD_PAYPAL, _('Paypal')),
        (PAYMENT_METHOD_CASH, _('Cash'))
    )
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("name"), max_length=100)
    method = models.IntegerField(choices=PAYMENT_METHOD_CHOICES, default=PAYMENT_METHOD_UNKNOWN)
    description = models.TextField(_("description"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # user = models.OneToOneField(Profile, on_delete=models.CASCADE)
    # payment_method = models.IntegerField(choices=PAYMENT_METHOD_CHOICES, default=PAYMENT_METHOD_UNKNOWN)
    # account_name = models.CharField(_("account name"), max_length=250)
    # account_number = models.CharField(_("account number"), max_length=100)
    # bank = models.CharField(_("bank"), max_length=100)
    # paypal_email = models.EmailField(_("paypal email"), max_length=255, blank=True, null=True)
    # expiry_date = models.DateField(_("expiry date"), blank=True, null=True)
    # cvv = models.CharField(_("cvv"), max_length=3, blank=True, null=True)
    # create_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'payment_method'
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'


class Wallet(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(Profile, on_delete=models.CASCADE)
    balance_point = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance_cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField()
    currency_id = models.OneToOneField(PaymentMethod, on_delete=models.CASCADE, blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'wallet'
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'

    def get_update_url(self):
        return reverse('account_transfer', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        self.balance_point = round(self.balance_point, 2)
        super(Wallet, self).save(*args, **kwargs)

    def deposit(self, value, type=''):
        admin_user = get_user_model().objects.get(is_superuser=True)
        if not admin_user:
            raise ValueError("No admin user found")
        print('admin_user', admin_user)
        admin_wallet = admin_user.wallet
        if admin_wallet.balance_point < value:
            raise ValueError("Admin wallet does not have enough balance")

        admin_wallet.balance_point -= value
        admin_wallet.save()

        self.balance_point += value
        self.save()

        transaction = self.transaction_set.create(
            transaction_type=Transaction.TRANSACTION_TYPE_DEPOSIT,
            wallet=self,
            status=Transaction.STATUS_COMPLETED,
            user_id_from=admin_user,
            user_id_to=self.user,
            description=type,
            create_at=timezone,
            update_at=timezone
        )

        SubTransaction.objects.create(
            transaction_id=transaction,
            wallet_id_from=admin_user.wallet,
            wallet_id_to=self,
            amount_cash=value,
            amount_point=value,
            description=type,
            status=Transaction.STATUS_COMPLETED,
            create_at=timezone,
            update_at=timezone
        )

    def withdraw(self, value):
        admin_user = get_user_model().objects.get(is_superuser=True)
        if not admin_user:
            raise ValueError("No admin user found")

        admin_wallet = admin_user.wallet
        if self.balance_point < value:
            raise ValueError("Wallet does not have enough balance")

        self.balance_point -= value
        self.save()

        admin_wallet.balance_point += value
        admin_wallet.save()

        transaction = self.transaction_set.create(
            transaction_type=Transaction.TRANSACTION_TYPE_WITHDRAW,
            wallet=self,
            status=Transaction.STATUS_COMPLETED,
            user_id_from=self.user,
            user_id_to=admin_user,
            description='Withdraw',
            create_at=timezone,
            update_at=timezone
        )

        SubTransaction.objects.create(
            transaction_id=transaction,
            wallet_id_from=self,
            wallet_id_to=admin_user.wallet,
            amount_cash=value,
            amount_point=value,
            description='Withdraw',
            status=Transaction.STATUS_COMPLETED,
            create_at=timezone,
            update_at=timezone)

    def transfer(self, wallet, value):
        self.withdraw(value)
        wallet.deposit(value)


class Transaction(models.Model):
    TRANSACTION_TYPE_DEPOSIT = 1
    TRANSACTION_TYPE_WITHDRAW = 2
    TRANSACTION_TYPE_CHOICES = (
        (TRANSACTION_TYPE_DEPOSIT, 'deposit'),
        (TRANSACTION_TYPE_WITHDRAW, 'withdraw')
    )
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = (
        (STATUS_PENDING, 'pending'),
        (STATUS_COMPLETED, 'completed'),
        (STATUS_REJECTED, 'rejected')
    )
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_PENDING)
    user_id_from = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver', blank=True, null=True)
    user_id_to = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='creator', blank=True, null=True)
    description = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.wallet.user.username

    # def save(self, *args, **kwargs):
    #     # ensure that the database only stores 2 decimal places
    #     self.amount = round(self.amount, 2)
    #     super(Transaction, self).save(*args, **kwargs)

    class Meta:
        db_table = 'transaction'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'


class SubTransaction(models.Model):
    TRANSACTION_TYPE_DEPOSIT = 1
    TRANSACTION_TYPE_WITHDRAW = 2
    TRANSACTION_TYPE_CHOICES = (
        (TRANSACTION_TYPE_DEPOSIT, 'deposit'),
        (TRANSACTION_TYPE_WITHDRAW, 'withdraw')
    )

    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = (
        (STATUS_PENDING, 'pending'),
        (STATUS_COMPLETED, 'completed'),
        (STATUS_REJECTED, 'rejected')
    )

    transaction_id = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    wallet_id_from = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='receiver', blank=True, null=True)
    wallet_id_to = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='creator', blank=True, null=True)
    amount_cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_point = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_PENDING)
    description = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.transaction.wallet.user.username

    class Meta:
        db_table = 'sub_transaction'
        verbose_name = 'Sub Transaction'
        verbose_name_plural = 'Sub Transactions'


class CartPayment(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE)
    account_name = models.CharField(_("account name"), max_length=250)
    account_number = models.CharField(_("account number"), max_length=100)
    bank = models.CharField(_("bank"), max_length=100)
    paypal_email = models.EmailField(_("paypal email"), max_length=255, blank=True, null=True)
    expiry_date = models.DateField(_("expiry date"), blank=True, null=True)
    cvv = models.CharField(_("cvv"), max_length=3, blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Event(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50)
    event_date = models.DateField(auto_now_add=True)
