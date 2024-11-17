document.addEventListener('DOMContentLoaded', () => {
    const isHomePage = window.location.pathname === '/employee/home/';

    if (isHomePage) {
        showLoading();
        initializeLocation();
    } else {
        const savedLat = localStorage.getItem('formatted_address');
        const addressInput = document.getElementById('id_address');
        addressInput.innerText = savedLat;
        addressInput.classList.add('highlight');

        hideLoading();
    }
});

function initializeLocation() {
    const savedLat = localStorage.getItem('latitude');
    const savedLng = localStorage.getItem('longitude');
    console.log('Saved location:', savedLat, savedLng);
    if (savedLat && savedLng) {
        console.log('Using saved location...');
        updateLocationAndFetchRestaurants(savedLat, savedLng);
    } else {
        console.log('Getting location...');
        getCurrentLocation()
            .then(({lat, lng}) => {
                console.log('Updating location...', lat, lng);
                localStorage.setItem('latitude', lat);
                localStorage.setItem('longitude', lng);
                updateLocationAndFetchRestaurants(lat, lng);
            })
            .catch(error => {
                console.error('Geolocation error:', error);
                document.getElementById('loading').textContent = 'Không thể xác định được vị trí của bạn.';
            });
    }
}

function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            return reject(new Error('Geolocation not supported'));
        }
        navigator.geolocation.getCurrentPosition(
            position => resolve({
                lat: position.coords.latitude,
                lng: position.coords.longitude
            }),
            reject,
            {enableHighAccuracy: true, timeout: 5000, maximumAge: 0}
        );
    });
}

function updateLocationAndFetchRestaurants(lat, lng) {
    updateDeliveryLocation(lat, lng);
    fetchRestaurants(lat, lng);
    updateLocationProfile(lat, lng);
}

function fetchRestaurants(lat, lng) {
    fetch(`/employee/home/?lat=${lat}&lng=${lng}`)
        .then(response => response.json())
        .then(data => {
            console.log('Data:', data);
            updateRestaurantList(data.vendors);

            updateRestaturantVIP(data.vendors_premium)
            hideLoading();
        })
        .catch(error => console.error('Error:', error));
}

function updateRestaurantList(vendors) {
    const vendorList = document.getElementById('vendorList');
    const restaurantList = document.getElementById('restaurantList');
    vendorList.innerHTML = '';
    restaurantList.innerHTML = '';

    if (vendors.length > 0) {
        vendorList.style.display = 'block';
        vendors.forEach(vendor => {
            const profilePicture = vendor.user_profile?.profile_picture?.url || '/static/employee/img/download.png';

            const vendorItem = `
                <li class="has-border">
                    <figure>
                        <a href="#"><img src="${profilePicture}" class="attachment-full size-full wp-post-image" alt=""></a>
                    </figure>
                </li>`;
            vendorList.insertAdjacentHTML('beforeend', vendorItem);

            const restaurantItem = `
                <li class="col-lg-6 col-md-6 col-sm-6 col-xs-12">
                    <div class="list-post featured">
                        <div class="img-holder">
                            <figure>
                                <a href="#"><img src="${profilePicture}" class="img-thumb wp-post-image" alt=""></a>
                            </figure>
                            <span class="restaurant-status close">
                                <em class="bookmarkRibbon"></em>Close
                            </span>
                        </div>
                        <div class="text-holder">
                            <div class="list-rating">
                                <div class="rating-star">
                                    <span class="rating-box" style="width: 100%;"></span>
                                </div>
                                <span class="reviews">(1)</span>
                            </div>
                            <div class="post-title">
                                <h5>
                                    <a href="listing-detail.html">${vendor.vendor_name}</a>
                                    <span class="sponsored text-color">Sponsored</span>
                                </h5>
                            </div>
                            <address>
                                ${vendor.address_line_1}, ${vendor.state}, ${vendor.city}
                            </address>
                        </div>
                    </div>
                </li>`;
            restaurantList.insertAdjacentHTML('beforeend', restaurantItem);
        });
    } else {
        const noVendorsMessage = `
<div class="container mx-auto p-4">
            <li class="no-vendors" style="    list-style-type: none;
">
    <figure style="text-align: center; padding: 20px;">
        <img src="/static/employee/img/download.png" alt="No Restaurants" class="no-vendors-img" style="width: 100px; height: 100px; margin-bottom: 10px;">
        <figcaption style="font-size: 16px; color: #555;"><div class="alert alert-warning" role="alert">
  No restaurants found near you.
</div></figcaption>
    </figure>
</li></div>`;
        vendorList.innerHTML = noVendorsMessage;
        restaurantList.innerHTML = noVendorsMessage;
    }
}

function updateRestaturantVIP(vendors_premium) {
    const vendorList = document.getElementById('vendorList');
    vendorList.innerHTML = '';

    if (vendors_premium.length > 0) {
        vendors_premium.forEach(vendor => {
            const profilePicture = vendor.user_profile?.profile_picture?.url || '/static/employee/img/download.png';
            const vendorItem = `
                <li class="has-border premium-vendor-item" style="    width: 228px !important;   padding: 20px; margin: 10px 15px 0 15px">
                    <figure class="premium-vendor-figure">
                        <a href="${vendor.get_absolute_url}" class="vendor-link">
                            <img src="${profilePicture}" class="vendor-img" alt="${vendor.vendor_name}">
                            <div class="premium-badge">VIP</div>
                        </a>
                        
                    </figure>
                    <div class="vendor-name" >
                        <a href="/marketplace/maketplace/${vendor.vendor_slug}" class="vendor-name-link">${vendor.vendor_name}</a>
                    </div>
                    <div class="best-choice">
                        BEST CHOICE
                    </div>
                    <a href="/marketplace/maketplace/${vendor.vendor_slug}" class="btn view-details">View Details</a>
                </li>`;
            vendorList.insertAdjacentHTML('beforeend', vendorItem);
        });
    } else {
        const noVendorsMessage = `
            <li class="no-vendors">
                <figure>
                    <img src="/static/employee/img/download.png" alt="No VIP Restaurants" class="no-vendors-img">
                    <figcaption>Không có nhà hàng VIP nào gần bạn.</figcaption>
                </figure>
            </li>`;
        vendorList.innerHTML = noVendorsMessage;
    }
}

function updateDeliveryLocation(lat, lng) {
    const geocoder = new google.maps.Geocoder();
    const latlng = {lat: parseFloat(lat), lng: parseFloat(lng)};

    geocoder.geocode({location: latlng}, (results, status) => {
        const addressInput = document.getElementById('id_address');
        console.log('addressInput', addressInput);
        if (status === 'OK' && results[0]) {
            console.log('Address:', results[0].formatted_address);
            addressInput.innerText = results[0].formatted_address;
            localStorage.setItem('formatted_address', results[0].formatted_address);

            addressInput.classList.add('highlight');
            setTimeout(() => addressInput.classList.remove('highlight'), 1000);
        } else {
            addressInput.textContent = 'Không thể lấy được địa chỉ của bạn.';
        }
    });
}

function updateLocationProfile(lat, lng) {

}

function hideLoading() {
    document.getElementById('loading_spinner').style.display = 'none';
    document.getElementById('loadingArea').style.display = 'none';
}

function showLoading() {
    console.log('Loading...');
    document.getElementById('loading_spinner').classList.remove('d-none');
    document.getElementById('loadingArea').classList.remove('d-none');
}
