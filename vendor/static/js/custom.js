let autocomplete;

function initAutocomplete() {
  console.log('initAutocomplete')
  autocomplete = new google.maps.places.Autocomplete(
    document.getElementById('id_address_line_1'), {
        types: ['geocode'],
        componentRestrictions: {country: 'us'}

  });
    autocomplete.addListener('place_changed', onPlaceChanged)
}
function onPlaceChanged() {
  var place = autocomplete.getPlace();
  if (!place.geometry) {
    document.getElementById('id_address_line_1').placeholder = 'Enter a location';
  }
  else {
    document.getElementById('latitude').value = place.geometry.location.lat();
    document.getElementById('longitude').value = place.geometry.location.lng();
  }
}
