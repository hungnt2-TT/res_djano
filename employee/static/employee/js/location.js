document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded fired.');

    const isHomePage = window.location.pathname === '/employee/home/';
    const addressInput = document.getElementById('id_address');
    const currentLocation = sessionStorage.getItem('current_location');

    if (currentLocation) {
        console.log('Using location from sessionStorage:', currentLocation);
        addressInput.innerText = currentLocation;
    }

    if (isHomePage) {
        initializeLocation();
    }
});

let locationInitialized = false;

function initializeLocation() {
    if (locationInitialized) {
        console.log('Location already initialized.');
        return;
    }

    console.log('Initializing location...');
    locationInitialized = true;

    getCurrentLocation()
        .then(({lat, lng}) => {
            updateDeliveryLocation(lat, lng);
        })
        .catch(error => {
            console.error('Geolocation error:', error);
            document.getElementById('loading').textContent = 'Không thể xác định được vị trí của bạn.';
        });
}

function updateDeliveryLocation(lat, lng) {
    const geocoder = new google.maps.Geocoder();
    const latlng = {lat: parseFloat(lat), lng: parseFloat(lng)};
    const params = new URLSearchParams(window.location.search);

    if (params.has('lat') && params.has('lng')) {
        console.log('Lat and Lng already in URL, skipping reload');
        return;
    }

    geocoder.geocode({location: latlng}, (results, status) => {
        if (status === 'OK' && results[0]) {
            const addressInput = document.getElementById('id_address');
            const currentLocation = results[0].formatted_address;

            console.log('Current location:', currentLocation);

            addressInput.innerText = currentLocation;
            addressInput.classList.add('highlight');

            sessionStorage.setItem('current_location', currentLocation);

            params.set('lat', lat);
            params.set('lng', lng);
            window.history.replaceState({}, '', `${window.location.pathname}?${params.toString()}`);

            // Xóa hiệu ứng sau 1 giây
            setTimeout(() => addressInput.classList.remove('highlight'), 1000);
        } else {
            console.error('Unable to fetch address');
            addressInput.textContent = 'Không thể lấy được địa chỉ của bạn.';
        }
    });
}

function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                position => {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    console.log('Current coordinates:', lat, lng);
                    resolve({lat, lng});
                },
                error => {
                    reject(error);
                }
            );
        } else {
            reject(new Error('Geolocation is not supported by this browser.'));
        }
    });
}
