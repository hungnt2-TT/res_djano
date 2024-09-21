from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from employee.models import Profile
import uuid
from django.urls import reverse

CURRENCY_STORE_FIELD = getattr(settings,
                               'WALLET_CURRENCY_STORE_FIELD', models.BigIntegerField)


class PaymentMethod(models.Model):
    PAYMENT_METHOD_UNKNOWN = 0
    PAYMENT_METHOD_BANK_TRANSFER = 1
    PAYMENT_METHOD_PAY = 2
    PAYMENT_METHOD_CHOICES = (
        (PAYMENT_METHOD_UNKNOWN, 'unknown'),
        (PAYMENT_METHOD_BANK_TRANSFER, 'bank transfer'),
        (PAYMENT_METHOD_PAY, 'pay')
    )
    user = models.OneToOneField(Profile, on_delete=models.CASCADE)
    payment_method = models.IntegerField(choices=PAYMENT_METHOD_CHOICES, default=PAYMENT_METHOD_UNKNOWN)
    account_name = models.CharField(_("account name"), max_length=250)
    account_number = models.CharField(_("account number"), max_length=100)
    bank = models.CharField(_("bank"), max_length=100)
    paypal_email = models.EmailField(_("paypal email"), max_length=255, blank=True, null=True)
    expiry_date = models.DateField(_("expiry date"), blank=True, null=True)
    cvv = models.CharField(_("cvv"), max_length=3, blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'payment_method'
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'


# Create your models here.
class Wallet(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(Profile, on_delete=models.CASCADE)
    balance = CURRENCY_STORE_FIELD(default=0)
    payment_method = models.OneToOneField(PaymentMethod, on_delete=models.CASCADE, blank=True, null=True)
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
        # ensure that the database only stores 2 decimal places
        self.balance = round(self.balance, 2)
        super(Wallet, self).save(*args, **kwargs)

    def deposit(self, value):
        self.transaction_set.create(
            transaction_type=Transaction.TRANSACTION_TYPE_DEPOSIT,
            value=value,
            running_balance=self.balance + value,
            description='Deposit'
        )
        self.balance += value
        self.save()

    def withdraw(self, value):
        self.transaction_set.create(
            transaction_type=Transaction.TRANSACTION_TYPE_WITHDRAW,
            value=value,
            running_balance=self.balance - value,
            description='Withdraw'
        )
        self.balance -= value
        self.save()

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
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE_CHOICES)
    value = CURRENCY_STORE_FIELD(default=0)
    running_balance = CURRENCY_STORE_FIELD(default=0)
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver', blank=True, null=True)
    creator = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='creator', blank=True, null=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.wallet.user.username

    def save(self, *args, **kwargs):
        # ensure that the database only stores 2 decimal places
        self.amount = round(self.amount, 2)
        super(Transaction, self).save(*args, **kwargs)

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
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.transaction.wallet.user.username

    class Meta:
        db_table = 'sub_transaction'
        verbose_name = 'Sub Transaction'
        verbose_name_plural = 'Sub Transactions'
