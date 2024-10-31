from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from django.conf import settings
from .models import Transaction, SubTransaction
import time


@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    print('paypal_payment_received', sender)
    time.sleep(5)
    ipn_obj = sender
    print('ipn_obj', ipn_obj)
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        if ipn_obj.receiver_email != settings.PAYPAL_RECEIVER_EMAIL:
            return
        print('paypal_payment_received', sender)
        transaction = Transaction.objects.create(
            transaction_type=Transaction.TRANSACTION_TYPE_DEPOSIT,
            wallet_id=ipn_obj.custom,
        )
        print('transaction', transaction)
        if transaction.status == Transaction.STATUS_PENDING:
            transaction.status = Transaction.STATUS_COMPLETED
            transaction.save()
            SubTransaction.objects.create(
                transaction_id=transaction,
                wallet_id_from=transaction.wallet,
                wallet_id_to=transaction.wallet,
                amount_cash=transaction.amount_cash,
                amount_point=transaction.amount_point,
                description=transaction.description,
                status=Transaction.STATUS_COMPLETED,
                create_at=transaction.create_at,
                update_at=transaction.update_at
            )
        else:
            print('paypal_payment_received', sender)
    else:
        print('paypal_payment_failed', sender)

print('paypal_payment_received')
# valid_ipn_received.connect(paypal_payment_received)
