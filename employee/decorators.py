# decorators.py
from django.core.exceptions import PermissionDenied


def restrict_employee_types(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.employee_type in [1, 2, 5]:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return _wrapped_view
