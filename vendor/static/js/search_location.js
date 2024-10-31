function initSearchLocation() {
    const input = document.getElementById('search_box'); // Lấy thẻ input thay vì giá trị
    console.log("input=>", input)
    const autocomplete = new google.maps.places.Autocomplete(input, {
        center: {
            lat: 48,
            lng: 4
        },
        componentRestrictions: {'country': ['vn']}
    });


    autocomplete.addListener('place_changed', function () {
        const place = autocomplete.getPlace();
        if (!place.geometry) {
            console.log("No details available for input: '" + place.name + "'");
            return;
        }

        const addressComponents = place.address_components;
        if (!addressComponents || addressComponents.length === 0) {
            console.log("No address components found");
            return;
        }

        const city = addressComponents[0]?.long_name || '';
        const latitude = place.geometry.location.lat();
        const longitude = place.geometry.location.lng();

        document.getElementById('id_address').value = city;
        document.getElementById('id_latitude').value = latitude;
        document.getElementById('id_lngitude').value = longitude;
    });
}

window.onload = function () {
    initSearchLocation();
}
