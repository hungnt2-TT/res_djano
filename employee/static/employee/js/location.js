document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('loading_spinner').classList.remove('d-none');
    document.getElementById('loadingArea').classList.remove('d-none');
    console.log('Getting location...');
    if (navigator.geolocation) {

        navigator.geolocation.getCurrentPosition(function (position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                console.log('Latitude:', lat);
                if (lat && lng) {
                    console.log('Updating location...', lat, lng);
                    updateDeliveryLocation(lat, lng);
                    fetch(`/employee/home/?lat=${lat}&lng=${lng}`)
                        .then(response => response.json())
                        .then(data => {
                            updateRestaurantList(data.vendors);
                            document.getElementById('loading_spinner').style.display = 'none';
                            document.getElementById('loadingArea').style.display = 'none';
                        })
                        .catch(error => console.error('Error:', error));
                }
            }, function (error) {
                console.error('Geolocation error:', error);
                document.getElementById('loading').textContent = 'Không thể xác định được vị trí của bạn.';
            },
            {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            }
        );
    }
});

function updateRestaurantList(vendors) {
    const vendorList = document.getElementById('vendorList');
    const restaurantList = document.getElementById('restaurantList');

    // Xóa nội dung cũ
    vendorList.innerHTML = '';
    restaurantList.innerHTML = '';

    // Nếu có vendors, hiển thị danh sách
    if (vendors.length > 0) {
        vendorList.style.display = 'block';  // Hiển thị vendor list nếu có vendor

        vendors.forEach(vendor => {
            // Kiểm tra xem user_profile có tồn tại không
            const profilePicture = vendor.user_profile && vendor.user_profile.profile_picture
                ? vendor.user_profile.profile_picture.url
                : '/static/employee/img/download.png';

            // Thêm vào ul#vendorList
            const vendorItem = `
                <li class="has-border">
                    <figure>
                        <a href="#"><img src="${profilePicture}" class="attachment-full size-full wp-post-image" alt=""></a>
                    </figure>
                </li>
            `;
            vendorList.insertAdjacentHTML('beforeend', vendorItem);

            // Thêm vào ul#restaurantList
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
                </li>
            `;
            restaurantList.insertAdjacentHTML('beforeend', restaurantItem);
        });
    } else {
        vendorList.innerHTML = '<li>Không có nhà hàng nào gần bạn.</li>';
        restaurantList.innerHTML = '<li>Không có nhà hàng nào gần bạn.</li>';
    }
}

function updateDeliveryLocation(lat, lng) {
    const geocoder = new google.maps.Geocoder();
    const latlng = {lat: parseFloat(lat), lng: parseFloat(lng)};
    geocoder.geocode({location: latlng}, (results, status) => {
        if (status === 'OK' && results[0]) {
            console.log('Address:', results[0].formatted_address);
            const addressInput = document.getElementById('id_address');
            addressInput.value = results[0].formatted_address;
            addressInput.classList.add('highlight');

            setTimeout(() => {
                addressInput.classList.remove('highlight');
            }, 7000);
        } else {
            location.textContent = 'Không thể lấy được địa chỉ của bạn.';
        }
    });
}
