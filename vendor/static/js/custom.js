let autocomplete;

function initAutocomplete() {
  autocomplete = new google.maps.places.Autocomplete(
    document.getElementById('autocomplete'), {types: ['geocode']});
  autocomplete.addListener('place_changed', fillInAddress);
}
function onPlaceChanged() {
  var place = autocomplete.getPlace();
  if (!place.geometry) {
    document.getElementById('autocomplete').placeholder = 'Enter a location';
  }
}