function createMarker(place, map) {
  return new google.maps.Marker({
    map: map,
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

  if (places[0].address_components.length > 3){
    document.getElementById('id_state').value = places[0].address_components[2].long_name;
    document.getElementById('id_city').value = places[0].address_components[3].long_name;
  }
  else {
    document.getElementById('id_state').value = places[0].address_components[1].long_name;
    document.getElementById('id_city').value = places[0].address_components[2].long_name;
  }

  document.getElementById('loc_latitude').value = places[0].geometry.location.lat();
  document.getElementById('loc_longitude').value = places[0].geometry.location.lng();
}

function initAutocomplete() {
  const map = new google.maps.Map(document.getElementById('map'), {
    center: {
      lat: 48,
      lng: 4
    },
    zoom: 150,
    disableDefaultUI:true
  });

  const input = document.getElementById('my-input-searchbox');
  const searchBox = new google.maps.places.SearchBox(input, {
    types: ['geocode', 'establishment', 'address', 'food'],
    componentRestrictions: {
      'country': ['vn']
    }
  });

  map.controls[google.maps.ControlPosition.TOP_CENTER].push(input);

  map.addListener('bounds_changed', function() {
    searchBox.setBounds(map.getBounds());
  });

  let markers = [];

  searchBox.addListener('places_changed', function() {
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