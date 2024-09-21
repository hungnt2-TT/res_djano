from django.shortcuts import render

from vendor.models import Vendor


# Create your views here.
def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count
    }
    return render(request, 'listings.html', context)


def vendor_detail(request, vendor_slug):
    print(request)
    print('vendor_slug', vendor_slug)
    vendor = Vendor.objects.get(vendor_slug=vendor_slug)
    context = {
        'vendor': vendor
    }
    return render(request, 'vendor_detail.html', context)
