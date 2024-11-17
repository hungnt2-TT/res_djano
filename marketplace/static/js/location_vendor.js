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
// <ul className="location-list">
//     {% for vendor in vendor_locations %}
//     <li className="location-item" onClick="openInfoWindow({{ forloop.counter0 }})">
//         <img src="{{ vendor.image_url }}" alt="{{ vendor.vendor_name }}"
//              style="width: 100%; height: auto; border-radius: 4px; margin-bottom: 0.5rem;"/>
//         <h3>{{vendor.vendor_name}}</h3>
//         <p>{{vendor.address_line_1}}</p>
//     </li>
//     {% empty %}
//     <li>No locations found.</li>
//     {% endfor %}
// </ul>
//
// <script>
//     let map;
//     let infoWindow;
//     let markers = [];
//
//     function initMap() {
//     const center = {lat: 21.0285, lng: 105.8542};
//
//     map = new google.maps.Map(document.getElementById('map'), {
//     zoom: 12,
//     center: center,
//     disableDefaultUI: true
// });
//
//     infoWindow = new google.maps.InfoWindow();
//
//     const vendors = JSON.parse('{{ vendors|safe }}');
//
//     vendors.forEach((vendor, index) => {
//     const latLng = {lat: parseFloat(vendor.latitude), lng: parseFloat(vendor.longitude)};
//     const marker = new google.maps.Marker({
//     position: latLng,
//     map: map,
//     draggable: true,
//     icon: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
//     title: vendor.vendor_name,
// });
//
//     marker.addListener('click', function () {
//     const contentString = `
//                 <div class="info-content">
//                     <h3>${vendor.vendor_name}</h3>
//                     <p><strong>Address:</strong> ${vendor.address_line_1}</p>
//                 </div>
//                 `;
//     infoWindow.setContent(contentString);
//     infoWindow.open(map, marker);
// });
//
//     markers.push(marker);
// });
// }
//
//     function openInfoWindow(index) {
//     const marker = markers[index];
//     const vendor = JSON.parse('{{ vendors|safe }}')[index];
//     const contentString = `
//         <div class="info-content">
//             <h3>${vendor.vendor_name}</h3>
//             <p><strong>Address:</strong> ${vendor.address_line_1}</p>
//         </div>
//         `;
//     infoWindow.setContent(contentString);
//     infoWindow.open(map, marker);
//     map.setCenter(marker.getPosition());
//     map.setZoom(15);
// }
//
//     window.onload = function () {
//     initMap();
// }
