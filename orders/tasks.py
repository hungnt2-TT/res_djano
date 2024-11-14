from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from menu.models import Coupon
from wallet.models import Wallet, Transaction, SubTransaction
from .models import Order


@shared_task
def process_order(order_id):
    print('order_id', order_id)
    validate_order_task.apply_async(args=[order_id], link=process_payment_task.s(order_id))
    print('order_id', order_id)
    process_payment_task.apply_async(args=[order_id], link=track_delivery_status_task.s(order_id))
    print('order_id', order_id)
    track_delivery_status_task.apply_async(args=[order_id], countdown=1800)
    print('order_id', order_id)
    complete_order_task.apply_async(args=[order_id], countdown=86400)


@shared_task
def validate_order_task(order_id):
    try:
        order_id = int(order_id)
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return f"Invalid order ID: {order_id}"

    if order.coupon_id and order.coupon_id != 0 and order.coupon_id is not None:
        coupon = Coupon.objects.filter(id=order.coupon_id).first()
        if not coupon or not coupon.is_valid():
            order.status = "Cancelled"
            order.message_error = "Coupon not valid"
            return "Invalid Coupon"

        if coupon.user and coupon.user != order.user:
            order.status = "Cancelled"
            order.message_error = "Coupon not valid for this user"
            order.save()
            return "Coupon not valid for this user"
        print('coupon', coupon)
        print('coupon', coupon.user)
        redeemed = coupon.successfully_redeemed(order.user)
        if not redeemed:
            order.status = "Cancelled"
            order.message_error = "Coupon already redeemed"
            order.save()
            return "Coupon already redeemed"
        order.status = "Waiting for Confirmation"
        redeemed.save()
        return "Order Validated"
    else:
        return "Order not using coupon"


@shared_task
def process_payment_task(order_id, *args, **kwargs):
    try:
        order_id = int(order_id)
        order = Order.objects.get(id=order_id)
    except (ValueError, Order.DoesNotExist):
        return f"Invalid order ID: {order_id}"
    payment_result = False
    if int(order.payment_method) == 2:
        from django.db import transaction
        try:
            with transaction.atomic():
                print('order.user', order.user)
                user_wallet = Wallet.objects.get(user=order.user)
                print('user_wallet', user_wallet)
                if user_wallet.balance_point < order.total:
                    order.status = "Cancelled"
                    order.message_error = "Insufficient balance in user's wallet"
                    order.save()
                    return "Insufficient balance"
                admin_wallet = Wallet.objects.get(user__is_superuser=True)
                print('admin_wallet', admin_wallet)
                user_wallet.balance_point -= order.total
                admin_wallet.balance_point += order.total
                user_wallet.save()
                admin_wallet.save()

            transactions = Transaction.objects.create(
                transaction_type=Transaction.TRANSACTION_TYPE_WITHDRAW,
                wallet=user_wallet,
                status=Transaction.STATUS_COMPLETED,
                user_id_from=order.user,
                user_id_to=admin_wallet.user,
                description="Payment from wallet",
                create_at=timezone.now(),
                update_at=timezone.now()
            )
            SubTransaction.objects.create(
                transaction_id=transactions,
                wallet_id_from=user_wallet,
                wallet_id_to=admin_wallet,
                amount_cash=0,
                amount_point=order.total,
                description='Payment from wallet to admin',
                status=transactions.STATUS_COMPLETED,
                create_at=timezone.now(),
                update_at=timezone.now()
            )
            payment_result = True
            order.status = "Payment Completed"
            order.is_payment_completed = True
            order.save()
            return "Payment Processed"
        except Wallet.DoesNotExist:
            order.status = "Cancelled"
            order.message_error = "User's wallet not found"
            order.save()
            return "Wallet not found"
    elif int(order.payment_method) == 3:
        try:
            from django.db import transaction
            with transaction.atomic():
                user_wallet = Wallet.objects.get(user=order.user)
                admin_wallet = Wallet.objects.get(user__is_superuser=True)

                # Create a transaction record for PayPal payment
                transaction_instance = Transaction.objects.create(
                    transaction_type=Transaction.TRANSACTION_TYPE_DEPOSIT,
                    wallet=user_wallet,
                    status=Transaction.STATUS_PENDING,
                    user_id_from=order.user,
                    user_id_to=admin_wallet.user,
                    description="Payment via PayPal",
                    create_at=timezone.now(),
                    update_at=timezone.now()
                )

                # Create a sub-transaction record
                SubTransaction.objects.create(
                    transaction_id=transaction_instance,
                    wallet_id_from=user_wallet,
                    wallet_id_to=admin_wallet,
                    amount_cash=order.total,
                    amount_point=0,
                    description='Payment via PayPal to admin',
                    status=Transaction.STATUS_PENDING,
                    create_at=timezone.now(),
                    update_at=timezone.now()
                )

                order.status = "Processing Payment"
                order.save()
                return "Payment Processed"
        except Wallet.DoesNotExist:
            order.status = "Cancelled"
            order.message_error = "User's wallet not found"
            order.save()
            return "Wallet not found"
    else:
        order.status = "Waiting for Confirmation"
        order.save()
        return "Payment Processed"


#
# @shared_task
# def prepare_shipping_task(order_id):
#     order = Order.objects.get(id=order_id)
#
#     shipping_info = order.create_shipping_label()
#
#     if shipping_info:
#         order.status = "Ready to Ship"
#         order.shipping_label = shipping_info
#     else:
#         order.status = "Shipping Failed"
#     order.save()
#     return "Shipping Prepared"


@shared_task
def notify_user_task(order_id, status):
    order_id = int(order_id)
    order = Order.objects.get(id=order_id)
    user = order.user

    user.send_email_notification(order_number=order.order_number, status=status)
    return "Notification Sent"


@shared_task
def track_delivery_status_task(order_id, *args, **kwargs):
    try:
        order_id = int(order_id)  # Đảm bảo order_id là số nguyên
    except ValueError:
        return f"Invalid order ID: {order_id}"

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return f"Order does not exist: {order_id}"

    delivery_status = order.check_delivery_status()

    if delivery_status == "Delivered":
        order.status = "Completed"
    elif delivery_status == "In Transit":
        order.status = "In Transit"
    else:
        order.status = "Cancelled"
        order.message_error = "Delivery Failed"

    order.save()
    return "Delivery Status Updated"


@shared_task
def complete_order_task(order_id):
    order_id = int(order_id)
    order = Order.objects.get(id=order_id)
    user_profile = order.user.profile
    # cart_items = Cart.objects.filter(user=order.user, is_ordered=False)
    if order.status != "Completed":
        return "Order not yet delivered"
    order.status = "Completed"
    order.save()

    # Gửi thông báo cho người dùng
    notify_user_task.delay(order_id, "Your order has been completed.")
    return "Order Completed"
