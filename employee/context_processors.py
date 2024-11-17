from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404

from employee.models import Profile
from res import settings

from employee.views import logout_user, get_pending_orders_for_vendor, get_pending_orders_for_shipper
from vendor.models import Vendor


def get_vendor(request):
    if (isinstance(request.user, AnonymousUser)
            or request.user.is_admin or
            request.user.employee_type != '2'):
        return {'vendor': None}
    else:
        vendor = get_object_or_404(Vendor, user=request.user, is_approved=True)
        return {'vendor': vendor}


def get_paypal_client_id(request):
    return {'paypal_client_id': settings.PAYPAL_CLIENT_ID}


def role(request):
    if isinstance(request.user, AnonymousUser):
        return {'role': 'guest'}
    else:
        return {'role': request.user.get_role()}


def request_order(request):
    user = request.user
    if not user.is_authenticated or user.employee_type != 1:
        return {'pending_orders_count': 0}
    vendor = Vendor.objects.get(user=user)
    pending_orders = get_pending_orders_for_vendor(vendor.id)
    return {'pending_orders_count': pending_orders.count()}


def request_shipper(request):
    user = request.user
    if not user.is_authenticated or user.employee_type != 5:
        return {'pending_ship_count': 0}
    shipper = user
    pending_orders = get_pending_orders_for_shipper(shipper.id)
    return {'pending_ship_count': pending_orders.count()}
