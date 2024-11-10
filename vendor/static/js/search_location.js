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

document.addEventListener('DOMContentLoaded', function () {
    const slider = document.querySelector('.slider');
    const nextBtn = document.querySelector('.next-btn');
    const prevBtn = document.querySelector('.prev-btn');

    const slideItems = document.querySelectorAll('.container-item');
    const totalItems = slideItems.length;
    console.log('Total items:', totalItems);
    const itemsPerSlide = 4; // Số lượng items hiển thị mỗi lần
    let currentIndex = 0; // Vị trí nhóm hiện tại

    // Hàm cập nhật vị trí slider
    function updateSlider() {

        slider.style.transform = `translateX(-${(currentIndex * (100 / itemsPerSlide))}%)`;
        console.log('TranslateX:', currentIndex * (100 / itemsPerSlide));
        console.log('Slider:', slider.style.transform);
        console.log('Current index:', currentIndex);

    }

    // Sự kiện khi nhấn nút Next
    nextBtn.addEventListener('click', function () {
        console.log('Current index:', currentIndex);
        console.log('Total items:', totalItems);
        console.log('Items per slide:', itemsPerSlide);
        if (currentIndex < totalItems - itemsPerSlide) {
            currentIndex++;
        } else {
            currentIndex = 0; // Nếu đã đến cuối thì quay lại đầu
        }
        updateSlider();
    });

    // Sự kiện khi nhấn nút Previous
    prevBtn.addEventListener('click', function () {
        if (currentIndex > 0) {
            currentIndex--;
        } else {
            currentIndex = totalItems - itemsPerSlide; // Quay lại nhóm cuối cùng
        }
        updateSlider();
    });

    // Khởi tạo slider ban đầu
    updateSlider();
});

window.onload = function () {
    initSearchLocation();
}
