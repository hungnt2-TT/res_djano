from django.urls import reverse


def detect_usertype(user):
    if user.employee_type == 1:
        redirect_url = reverse('owner_dashboard')
    elif user.employee_type == 2:
        redirect_url = reverse('customer_dashboard')
    elif user.employee_type == 5:
        redirect_url = reverse('shipper_dashboard')
    elif user.employee_type is None and user.is_superuser:
        redirect_url = reverse('admin:index')
    else:
        redirect_url = reverse('_login')
    return redirect_url


def conver_timezone_viettnam():
    from pytz import timezone
    from datetime import datetime
    vietnam = timezone('Asia/Ho_Chi_Minh')
    fmt = '%H:%M:%S'
    now = datetime.now(vietnam)
    return now.strftime(fmt)


def get_or_set_current_location(request):
    if 'lat' in request.session and 'lng' in request.session:
        lat = request.session['lat']
        lng = request.session['lng']
        return float(lat), float(lng)
    elif 'lat' in request.GET and 'lng' in request.GET:
        lat = request.GET['lat']
        lng = request.GET['lng']
        request.session['lat'] = lat
        request.session['lng'] = lng
        return float(lat), float(lng)
    elif 'current_location' in request.session:
        return request.session['current_location']
    else:
        return None
