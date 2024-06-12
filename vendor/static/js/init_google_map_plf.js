// let autocomplete;
//
// function initAutoComplete() {
//     // geocoder = new google.maps.Geocoder();
//     // console.log("geocoder=>", geocoder)
//     // var latlng = new google.maps.LatLng(53.3496, -6.3263);
//     //     console.log("latlng=>", latlng)
//     //
//     // var mapOptions =
//     //     {
//     //         zoom: 8,
//     //         center: latlng
//     //     }
//     // map = new google.maps.Map(document.getElementById('id_address_line_1'), mapOptions);
//     // console.log("map=>", map)
//     autocomplete = new google.maps.places.Autocomplete(
//         document.getElementById('id_address_line_1'),
//         {
//             types: ['geocode', 'establishment', 'address'],
//             componentRestrictions: {'country': ['vn']},
//         })
//     console.log("autocomplete=>", autocomplete)
//     autocomplete.addListener('place_changed', onPlaceChanged);
// }
//
// function onPlaceChanged() {
//     var place = autocomplete.getPlace();
//     console.log('place=>', place)
//     if (!place.geometry) {
//         console.log('place=>', place)
//
//         document.getElementById('id_address_line_1').placeholder = "Start typing...";
//     } else {
//         console.log('place name=>', place.name)
//     }
// }
// // var Ireland = "Dublin";
// //
// // function initAutoComplete()
// // {
// //   geocoder = new google.maps.Geocoder();
// //   var latlng = new google.maps.LatLng(53.3496, -6.3263);
// //   var mapOptions =
// //   {
// //     zoom: 8,
// //     center: latlng
// //   }
// //   map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
// //   codeAddress(Ireland);//call the function
// // }
// //
// // function codeAddress(address)
// // {
// //   geocoder.geocode( {address:address}, function(results, status)
// //   {
// //     if (status == google.maps.GeocoderStatus.OK)
// //     {
// //       map.setCenter(results[0].geometry.location);//center the map over the result
// //       //place a marker at the location
// //       var marker = new google.maps.Marker(
// //       {
// //           map: map,
// //           position: results[0].geometry.location
// //       });
// //     } else {
// //       alert('Geocode was not successful for the following reason: ' + status);
// //    }
// //   });
// // }

function initAutocomplete() {
  var map = new google.maps.Map(document.getElementById('map'), {
    center: {
      lat: 48,
      lng: 4
    },
    zoom: 4,
    disableDefaultUI:true
  });

  // Create the search box and link it to the UI element.
  var input = document.getElementById('my-input-searchbox');
  var searchBox = new google.maps.places.SearchBox(input,
      {
      types: ['geocode', 'establishment', 'address'],
      componentRestrictions: {
        'country': ['vn']
      }
    });
  map.controls[google.maps.ControlPosition.TOP_CENTER].push(input);

  // Bias the SearchBox results towards current map's viewport.
  map.addListener('bounds_changed', function() {
    searchBox.setBounds(map.getBounds());
  });

  var markers = [];
  // Listen for the event fired when the user selects a prediction and retrieve
  // more details for that place.
  searchBox.addListener('places_changed', function() {
    var places = searchBox.getPlaces();
    if (places.length == 0) {
      return;
    }
    // Clear out the old markers.
    markers.forEach(function(marker) {
      marker.setMap(null);
    });
    markers = [];
    // For each place, get the location.
    var bounds = new google.maps.LatLngBounds();
    places.forEach(function(place) {
      if (!place.geometry) {
        console.log("Returned place contains no geometry");
        return;
      }

      // Create a marker for each place.
      markers.push(new google.maps.Marker({
        map: map,
        position: place.geometry.location
      }));

      if (place.geometry.viewport) {
        // Only geocodes have viewport.
        bounds.union(place.geometry.viewport);
      } else {
        bounds.extend(place.geometry.location);
      }
    });
    map.fitBounds(bounds);
  });
}
document.addEventListener("DOMContentLoaded", function(event) {
  initAutocomplete();
});
