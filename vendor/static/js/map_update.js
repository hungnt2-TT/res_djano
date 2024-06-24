function createMarker(place, map) {
    console.log("place=>", place)
    return new google.maps.Marker({
        map: map, position: place.geometry.location
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
    console.log("places[0].address_components=>", places[0].address_components)
    console.log("document.getElementById('id_state').value", document.getElementById('id_state').value)

    if (places[0].address_components.length > 3) {
        document.getElementById('id_state').value = places[0].address_components[2].long_name;
        document.getElementById('id_city').value = places[0].address_components[3].long_name;
    } else {
        document.getElementById('id_state').value = places[0].address_components[1].long_name;
        document.getElementById('id_city').value = places[0].address_components[2].long_name;
    }
    console.log("document.getElementById('id_state').value", document.getElementById('id_state').value)
    console.log("places[0].geometry.location", places[0].geometry.location)
    document.getElementById('loc_latitude').value = places[0].geometry.location.lat();
    document.getElementById('loc_longitude').value = places[0].geometry.location.lng();
}

function initSearchBox() {
    let id_latitude = document.getElementById('id_latitude').value;
    let id_longitude = document.getElementById('id_longitude').value;
    const vendor_loc = new google.maps.LatLng(id_latitude, id_longitude);

    const map = new google.maps.Map(document.getElementById('map_'), {
        center: vendor_loc, zoom: 15,
        mapTypeId: 'roadmap', types: ['geocode', 'establishment', 'address', 'food'],
    });
    const input = document.getElementById('my-input-searchbox');
    const searchBox = new google.maps.places.SearchBox(input, {
        types: ['geocode', 'establishment', 'address', 'food'], componentRestrictions: {
            'country': ['vn']
        }
    });
    var newPlace = {
        geometry: {
            location: new google.maps.LatLng(id_latitude, id_longitude)
        }
    };

    createMarker(newPlace, map);
    setTimeout(function () {
        map.controls[google.maps.ControlPosition.TOP_CENTER].push(input);
    }, 1000);

    map.addListener('bounds_changed', function () {
        searchBox.setBounds(map.getBounds());
    });

    let markers = [];

    searchBox.addListener('places_changed', function () {
        console.log("searchBox=>")
        const places = searchBox.getPlaces();
        console.log("places====", places)
        if (places.length == 0) {
            return;
        }

        markers.forEach(marker => marker.setMap(null));
        markers = [];

        let bounds = new google.maps.LatLngBounds();
        places.forEach(place => {
            if (!place.geometry) {
                console.log("Returned place contains no geometry");
                return;
            }
            console.log("place=>", place)
            markers.push(createMarker(place, map));
            bounds = updateBounds(place, bounds);
        });

        updateFormFields(places);
        map.fitBounds(bounds);
    });
}

window.onload = function () {
    initSearchBox();
}
