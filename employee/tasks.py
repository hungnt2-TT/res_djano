from celery import shared_task
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point, GEOSGeometry
from django.utils import timezone
from django.db import transaction
from django.contrib.gis.db.models.functions import Distance

from employee.mails import send_mail
from employee.models import Profile, EmployeeProfile
from menu.models import Coupon
from orders.models import Order
from vendor.models import Vendor
from wallet.models import Wallet, Transaction, SubTransaction


@shared_task
def find_nearest_shipper(order_id, *args, **kwargs):
    try:
        order_id = int(order_id)
        order = Order.objects.get(id=order_id, status='Accepted')

        vendor = order.vendors.first()
        if not vendor:
            return f"No vendor found for this order: {order_id}"

        vendor_location = vendor.location
        vendor_point = GEOSGeometry(f'POINT({vendor.longitude} {vendor.latitude})', srid=4326)
        shipper = Profile.objects.filter(employee_type=5, is_active=True)
        print('shipper', shipper)
        nearest_shipper = EmployeeProfile.objects.filter(
            user__in=shipper,
            location__distance_lte=(vendor_point, 20000)
        ).exclude(user__in=[order.shipper for order in Order.objects.filter(status='Shipper Assigned')]).annotate(
            distance=Distance('location', vendor_point)
        ).order_by('distance').first()
        print('nearest_shipper', nearest_shipper)
        if nearest_shipper:
            send_order_request_to_shipper(order, nearest_shipper)

            order.status = 'Shipper Pending'
            order.shipper = nearest_shipper.user
            order.assigned_at = timezone.now()
            order.save()

            reassign_shipper_if_no_response.apply_async((order_id,), kwargs={'type': 'shipper_not_responding'},
                                                        countdown=600)

        else:
            order.status = 'Cancelled'
            order.message_error = 'No shipper available'
            order.save()

    except Order.DoesNotExist:
        return f"Invalid order ID: {order_id}"


@shared_task
def send_order_request_to_shipper(order, nearest_shipper):
    subject = "New Order Request"
    message = f"New order request from {order.user.nickname}"
    context = {
        'user': nearest_shipper.user,
        'message': message,
        'subject': subject,
        'order_number': order.order_number,
        'status': order.status,
    }
    print('Sending order request to:', nearest_shipper.user)
    print('email:', nearest_shipper.user.email)
    send_mail(subject, 'mails/notification_shipper.html', context)


@shared_task
def reassign_shipper_if_no_response(order_id, *args, **kwargs):
    try:
        order_id = int(order_id)
        type_of_rejection = kwargs.get('type', None)

        order = Order.objects.get(id=order_id)

        if order.attempts >= 3:
            order.status = 'Cancelled'
            order.message_error = 'Maximum attempts reached, no available shipper'
            order.save()
            return f"Order {order_id} cancelled due to maximum attempts"

        if type_of_rejection == 'shipper_rejected':
            order.status = 'Shipper Rejected'
            vendor = order.vendors.first()
            vendor_point = GEOSGeometry(f'POINT({vendor.longitude} {vendor.latitude})', srid=4326)
            next_shipper = Profile.objects.filter(
                user_type='Shipper',
                location__distance_lte=(vendor_point, 5000)
            ).exclude(user=order.shipper)

            next_shipper = next_shipper.exclude(
                user__in=[o.shipper for o in Order.objects.filter(status='Shipper Assigned')])

            next_shipper = next_shipper.annotate(
                distance=Distance('location', vendor_point)
            ).order_by('distance').first()

            if next_shipper:
                order.shipper = next_shipper.user
                order.assigned_at = timezone.now()
                order.status = 'Shipper Pending'
                order.attempts += 1
                order.save()

                reassign_shipper_if_no_response.apply_async((order_id,), kwargs={'type': 'shipper_not_responding'},
                                                            countdown=600)
            else:
                order.status = 'Cancelled'
                order.message_error = 'No available shipper found'
                order.save()

        elif type_of_rejection == 'shipper_not_responding':
            elapsed_time = timezone.now() - order.assigned_at

            if elapsed_time.total_seconds() > 600:
                vendor = order.vendors.first()
                vendor_point = GEOSGeometry(f'POINT({vendor.longitude} {vendor.latitude})', srid=4326)

                next_shipper = Profile.objects.filter(
                    user_type='Shipper',
                    location__distance_lte=(vendor_point, 5000)
                ).exclude(user=order.shipper)

                next_shipper = next_shipper.exclude(
                    user__in=[o.shipper for o in Order.objects.filter(status='Shipper Assigned')])

                next_shipper = next_shipper.annotate(
                    distance=Distance('location', vendor_point)
                ).order_by('distance').first()

                if next_shipper:
                    order.shipper = next_shipper.user
                    order.assigned_at = timezone.now()
                    order.attempts += 1
                    order.save()

                    reassign_shipper_if_no_response.apply_async((order_id,), kwargs={'type': 'shipper_not_responding'},
                                                                countdown=600)
                else:
                    order.status = 'Cancelled'
                    order.message_error = 'No available shipper found after multiple attempts'
                    order.save()

        else:
            order.status = 'Cancelled'
            order.message_error = 'No shipper available'
            order.save()

    except Order.DoesNotExist:
        return f"Invalid order ID: {order_id}"
    except Exception as e:
        return f"An error occurred: {str(e)}"
