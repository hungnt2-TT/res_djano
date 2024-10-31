from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404

from employee.views import logout_user
from vendor.models import Vendor


def get_vendor(request):
    if (isinstance(request.user, AnonymousUser)
            or request.user.is_admin or
            request.user.employee_type != '2'):
        return {'vendor': None}
    else:
        vendor = get_object_or_404(Vendor, user=request.user, is_approved=True)
        return {'vendor': vendor}
