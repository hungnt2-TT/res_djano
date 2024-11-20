from celery import shared_task

from menu.models import Coupon
from orders.models import Order
from orders.utils import extract_points
from vendor.models import Vendor
from wallet.models import Wallet


@shared_task
def process_payment_bank_shipper_task(order_id, *args, **kwargs):
    try:
        order_id = int(order_id)
        order = Order.objects.get(id=order_id)
    except (ValueError, Order.DoesNotExist):
        return f"Invalid order ID: {order_id}"

    # wallet - paypal
    if int(order.payment_method) == 2 or int(order.payment_method) == 3 or int(order.payment_method) == 1:
        from django.db import transaction
        try:
            with transaction.atomic():
                print('order.user', order.user)
                shipper_wallet = Wallet.objects.get(user=order.shipper)
                admin_wallet = Wallet.objects.get(user__is_superuser=True)
                vendor_id = order.get_vendor_by_order_details()
                vendor = Vendor.objects.get(id=vendor_id)
                print('vendor_id', vendor_id)
                vendor_wallet = Wallet.objects.get(user=vendor.user)
                print('vendor_wallet', vendor_wallet)
                print('admin_wallet', admin_wallet)
                shipper_wallet.deposit(order.total_shipping_cost, 'order_payment', 'Payment from user')
                vendor_wallet.deposit(order.subtotal, 'order_payment', 'Payment from user')
                if order.coupon_id:
                    coupon = Coupon.objects.get(id=order.coupon_id)
                    if coupon.type_of_discount == 'Refund Coin':
                        user_wallet = Wallet.objects.get(user=order.user)
                        print('order.coupon', order.coupon)
                        coupon = extract_points(order.coupon)
                        print('coupon', coupon)
                        user_wallet.deposit(coupon, 'point', "Refund coupon to user wallet")  # refund coin
            order.status = "Completed"
            order.save()
            return "Payment Processed"
        except Wallet.DoesNotExist as e:
            order.status = "cancelled"
            order.message_error = f"Wallet not found: {str(e)}"
            order.save()
            return "Order Cancelled"
        except ValueError as e:
            order.status = "failed"
            order.message_error = str(e)
            order.save()
            return "Payment Failed"
    elif int(order.payment_method) == 4:
        try:
            from django.db import transaction
            with transaction.atomic():
                shipper_wallet = Wallet.objects.get(user=order.shipper)
                coupon_extract = 0
                if order.coupon_id:
                    coupon = Coupon.objects.get(id=order.coupon_id)
                    if coupon.type_of_discount == 'Percentage' or coupon.type_of_discount == 'Free Delivery':
                        coupon_extract = extract_points(order.coupon)
                    elif coupon.type_of_discount == 'Refund Coin':
                        user_wallet = Wallet.objects.get(user=order.user)
                        coupon_extract_point = extract_points(order.coupon)
                        user_wallet.deposit(coupon_extract_point, 'point',
                                            "Refund coupon to user wallet")  # refund coin
                total_after_discount = order.total - coupon_extract
                shipper_paid_to_vendor = order.subtotal
                shipper_final_payment = (shipper_paid_to_vendor - total_after_discount + order.total_shipping_cost)
                shipper_wallet.deposit(shipper_final_payment, 'order_payment', 'Payment from shipper')
                order.status = "Completed"
                order.save()
                return "Payment Processed"

        except Wallet.DoesNotExist:
            order.status = "Cancelled"
            order.message_error = "Wallet not found for user or shipper"
            order.save()
            return "Order Cancelled"
        except Exception as e:
            print('error', e)
            order.status = "Error"
            order.message_error = f"Unexpected error: {str(e)}"
            order.save()
            return "Order Error"
    else:
        order.status = "Cancelled"
        order.message_error = "Invalid payment method"
        order.save()
        return "Order Cancelled"
