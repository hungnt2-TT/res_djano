def detect_usertype(user):
    if user.employee_type == 1:
        redirect_url = 'owner_dashboard'
        return redirect_url
    elif user.employee_type == 2:
        redirect_url = 'customer_dashboard'
        return redirect_url
    elif user.employee_type == 5:
        redirect_url = 'shipper_dashboard'
        return redirect_url
    elif user.employee_type is None and user.is_superuser:
        redirect_url = '/admin'
        return redirect_url
    else:
        redirect_url = '_login'
        return redirect_url
