function locationVendor() {
    const vendorLat = window.vendorLat;
    const vendorLng = window.vendorLng;
    const vendorLocation = window.vendorLocation;

    const vendor_location = new google.maps.LatLng(vendorLat, vendorLng);
    const map = new google.maps.Map(document.getElementById('map'), {
        center: vendor_location,
        zoom: 15,
        disableDefaultUI: true
    });

    const marker = new google.maps.Marker({
        map: map,
        position: vendor_location,
        title: 'Vendor location',
        draggable: true,
        icon: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'
    });
}

window.onload = function () {
    locationVendor();
}