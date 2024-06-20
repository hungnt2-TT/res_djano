from django.contrib.auth.models import AnonymousUser

from vendor.models import Vendor


def get_vendor(request):
    if isinstance(request.user, AnonymousUser):
        return {'vendor': None}
    elif request.user.is_admin:
        return {'vendor': None}
    else:
        return {'vendor': Vendor.objects.get(user=request.user)}
