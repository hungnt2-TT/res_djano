var componentForm = {
    street_number: 'long_name',
    route: 'long_name',
    administrative_area_level_2: 'long_name',
    administrative_area_level_1: 'long_name',
    postal_code: 'long_name',
};

function createMarker(place, map) {
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

function fillInAddress(places) {
    console.log("places=>", places)
    for (var component in componentForm) {
        document.getElementById(component).value = '';
        document.getElementById(component).disabled = false;
    }
    for (var i = 0; i < places[0].address_components.length; i++) {
        var addressType = places[0].address_components[i].types[0];
        var val;
        if (componentForm[addressType]) {
            val = places[0].address_components[i][componentForm[addressType]];
            document.getElementById(addressType).value = val;
        } else if (addressType !== 'postal_code') {
            document.getElementById('postal_code').value = '100000';
        }
    }
    $('#id_location').val(places[0].formatted_address);
    $('#id_latitude').val(places[0].geometry.location.lat());
    $('#id_longitude').val(places[0].geometry.location.lng());
}

function updateFormFields(places) {
    fillInAddress(places);
}

function initSearchBox() {
    const input = document.getElementById('my-input-searchbox');
    let id_latitude_elem = document.getElementById('id_latitude');
    let id_longitude_elem = document.getElementById('id_longitude');

    let id_latitude = id_latitude_elem ? id_latitude_elem.value : 0;
    let id_longitude = id_longitude_elem ? id_longitude_elem.value : 0;
    const vendor_loc = new google.maps.LatLng(id_latitude, id_longitude);

    const map = new google.maps.Map(document.getElementById('map_'), {
        center: vendor_loc, zoom: 15, mapTypeId: 'roadmap', types: ['geocode', 'establishment', 'address', 'food'],
    });
    const searchBox = new google.maps.places.SearchBox(input, {
        types: ['geocode', 'establishment', 'address', 'food'], componentRestrictions: {
            'country': ['vn']
        }
    });

    var newPlace = {
        geometry: {
            location: vendor_loc
        }
    };

    setTimeout(function () {
        map.controls[google.maps.ControlPosition.TOP_CENTER].push(input);
    }, 1000);

    map.addListener('bounds_changed', function () {
        searchBox.setBounds(map.getBounds());
    });

    let markers = [];
    markers.push(createMarker(newPlace, map))
    searchBox.addListener('places_changed', function () {
        const places = searchBox.getPlaces();
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
            markers.push(createMarker(place, map));
            bounds = updateBounds(place, bounds);
        });

        updateFormFields(places);
        map.fitBounds(bounds);
    });
}
