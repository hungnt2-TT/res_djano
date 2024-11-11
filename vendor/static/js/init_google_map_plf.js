function createMarker(place, map, icon, title) {
    return new google.maps.Marker({
        map: map,
        title: title,
        icon: icon,
        position: place.geometry.location
    });
}

function updateBounds(place, bounds) {
    if (place.geometry.viewport) {
        bounds.union(place.geometry.viewport);
    } else {
        bounds.extend(place.geometry.location);
    }
    return bounds;
}

function updateFormFields(places) {
    console.log("places=>", places)

    if (places[0].address_components.length > 3) {
        document.getElementById('id_state').value = places[0].address_components[2].long_name;
        document.getElementById('id_city').value = places[0].address_components[3].long_name;
    } else {
        document.getElementById('id_state').value = places[0].address_components[1].long_name;
        document.getElementById('id_city').value = places[0].address_components[2].long_name;
    }

    document.getElementById('loc_latitude').value = places[0].geometry.location.lat();
    document.getElementById('loc_longitude').value = places[0].geometry.location.lng();
}
function initAutocomplete() {
    const input = document.getElementById('my-input-searchbox');
    const savedLat = localStorage.getItem('latitude') || 21.028511;
    const savedLng = localStorage.getItem('longitude') || 105.804817;
    const vendor_location = new google.maps.LatLng(savedLat, savedLng);
    const map = new google.maps.Map(document.getElementById('map'), {
        center: vendor_location,
        zoom: 15,
        disableDefaultUI: true
    });

    // Initial marker with red icon
    const marker = new google.maps.Marker({
        map: map,
        position: vendor_location,
        title: 'Vendor location',
        draggable: true,
        icon: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'
    });

    const searchBox = new google.maps.places.SearchBox(input, {
        types: ['geocode', 'establishment', 'address', 'food'],
        componentRestrictions: {
            'country': ['vn']
        }
    });

    map.controls[google.maps.ControlPosition.TOP_CENTER].push(input);

    map.addListener('bounds_changed', function () {
        searchBox.setBounds(map.getBounds());
    });

    let markers = [];

    searchBox.addListener('places_changed', function () {
        const places = searchBox.getPlaces();

        if (places.length == 0) {
            return;
        }

        markers.forEach(marker => marker.setMap(null));
        markers = [];

        let bounds = new google.maps.LatLngBounds();
        places.forEach(place => {
            if (!place.geometry || !place.geometry.location) {
                console.log("Returned place contains no geometry");
                return;
            }
            const icon = {
                url: place.icon,
                size: new google.maps.Size(71, 71),
                origin: new google.maps.Point(0, 0),
                anchor: new google.maps.Point(17, 34),
                scaledSize: new google.maps.Size(25, 25),
            };
            markers.push(createMarker(place, map, icon, place.name));
            bounds = updateBounds(place, bounds);
        });

        updateFormFields(places);
        map.fitBounds(bounds);
    });
}

window.onload = function () {
    initAutocomplete();
}// function initAutocomplete() {
//     const input = document.getElementById('my-input-searchbox');
//     const savedLat = localStorage.getItem('latitude') || 21.028511;
//     const savedLng = localStorage.getItem('longitude') || 105.804817;
//     console.log("savedLat=>", savedLat)
//     console.log("savedLng=>", savedLng)
//     const vendor_location = new google.maps.LatLng(savedLat, savedLng);
//     console.log("vendor_location=>", vendor_location)
//     const map = new google.maps.Map(document.getElementById('map'), {
//         center: vendor_location,
//         zoom: 15,
//         disableDefaultUI: true
//     });
//     const market = new google.maps.Marker({
//         map: map,
//         position: vendor_location,
//         title: 'Vendor location',
//         draggable: true,
//     });
//     const searchBox = new google.maps.places.SearchBox(input, {
//         types: ['geocode', 'establishment', 'address', 'food'],
//         componentRestrictions: {
//             'country': ['vn']
//         }
//     });
//
//     map.controls[google.maps.ControlPosition.TOP_CENTER].push(input);
//
//     map.addListener('bounds_changed', function () {
//         searchBox.setBounds(map.getBounds());
//     });
//
//     let markers = [];
//
//     searchBox.addListener('places_changed', function () {
//         const places = searchBox.getPlaces();
//
//         if (places.length == 0) {
//             return;
//         }
//
//         markers.forEach(marker => marker.setMap(null));
//         markers = [];
//
//         let bounds = new google.maps.LatLngBounds();
//         places.forEach(place => {
//             if (!place.geometry || !place.geometry.location) {
//                 console.log("Returned place contains no geometry");
//                 return;
//             }
//             const icon = {
//                 url: place.icon,
//                 size: new google.maps.Size(71, 71),
//                 origin: new google.maps.Point(0, 0),
//                 anchor: new google.maps.Point(17, 34),
//                 scaledSize: new google.maps.Size(25, 25),
//             };
//             markers.push(createMarker(place, map, icon, place.name));
//             bounds = updateBounds(place, bounds);
//         });
//
//         updateFormFields(places);
//         map.fitBounds(bounds);
//     });
// }

window.onload = function () {
    initAutocomplete();
}

