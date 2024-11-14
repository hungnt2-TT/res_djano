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
        nearest_shipper = EmployeeProfile.objects.filter(
            user__in=shipper,
            location__distance_lte=(vendor_point, 5000)
        ).annotate(
            distance=Distance('location', vendor_point)
        ).order_by('distance').first()

        if nearest_shipper:
            send_order_request_to_shipper(order, nearest_shipper)

            order.status = 'Shipper Assigned'
            order.shipper = nearest_shipper.user
            order.assigned_at = timezone.now()
            order.save()

            reassign_shipper_if_no_response.apply_async((order_id,), countdown=600)

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
        'status': order.status
    }
    send_mail(subject, 'mails/notification_shipper.html', context)


@shared_task
def reassign_shipper_if_no_response(order_id, *args, **kwargs):
    try:
        order_id = int(order_id)
        order = Order.objects.get(id=order_id, status='Shipper Assigned')
        elapsed_time = timezone.now() - order.assigned_at
        if elapsed_time.total_seconds() > 600:
            vendor_location = order.vendor.location
            vendor_point = Point(vendor_location.longitude, vendor_location.latitude, srid=4326)
            next_shipper = Profile.objects.filter(
                user_type='Shipper',
                location__distance_lte=(vendor_point, 5000)
            ).exclude(user=order.shipper).annotate(
                distance=Distance('location', vendor_point)
            ).order_by('distance').first()

            order.shipper = next_shipper.user
            order.assigned_at = timezone.now()
            order.save()

            reassign_shipper_if_no_response.apply_async((order_id,), countdown=600)

        else:
            order.status = 'Cancelled'
            order.message_error = 'No shipper available'
            order.save()
    except Order.DoesNotExist:
        return f"Invalid order ID: {order_id}"
