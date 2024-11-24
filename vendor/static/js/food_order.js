$(document).ready(function () {
    // $('#foodForm').on('submit', function (e) {
    //     showLoading();
    //     e.preventDefault();
    //     let data = $('.ck-editor-container').find('.ck-content').html();
    //     let foodName = $('#food_name').val();
    //     let price = $('#price').val();
    //     let selectedCategory = $('#category').val();
    //     let isAvailable = $('#is_available').is(':checked');
    //     let formData = new FormData(this);
    //     let sizes = [];
    //     $('.size-selection select[data-food-id="]').each(function () {
    //         let sizeId = $(this).val();
    //         let price = $(this).closest('.size-selection').find('input[name="price"]').val();  // Lấy giá từ input
    //
    //         if (sizeId && price) {
    //             sizes.push({
    //                 'size_id': sizeId,
    //                 'price': price
    //             });
    //         }
    //     });
    //     formData.append('category_food', selectedCategory)
    //     formData.append('description', data)
    //     console.log('formData', formData);
    //     // $.ajax({
    //     //     type: 'POST',
    //     //     url: $(this).attr('action'),
    //     //     data: formData,
    //     //     processData: false,
    //     //     contentType: false,
    //     //     success: function (response) {
    //     //         alert(response.message, response.alert);
    //     //         $('#foodForm')[0].reset();
    //     //         $('#message').html('');
    //     //
    //     //     },
    //     //     error: function (response) {
    //     //         let errors = response.errors;
    //     //         let errorMessages = '<ul>';
    //     //         for (let field in errors) {
    //     //             errors[field].forEach(function (error) {
    //     //                 errorMessages += error + '<br>';
    //     //             });
    //     //         }
    //     //         $('#message').html('<div class="text-danger">' + errorMessages + '</div>');
    //     //         alert(response.message, response.alert);
    //     //     },
    //     //     complete: function () {
    //     //         demo().then(() => {
    //     //             hideLoading();
    //     //             location.reload();
    //     //         });
    //     //     }
    //     // });
    // });

    $('input[type="file"][id^="imageUpload"], input[type="file"][id^="imageUploadCover"]').change(function () {
        const fileInput = this;
        const food_id = fileInput.id.split('imageUploadCover')[1];

        if (fileInput.files && fileInput.files[0]) {
            readerFunction(fileInput, food_id);
        }
    });
    $(".edit-link").on('click', function (e) {
        e.preventDefault();
        let transactionId = $(this).data('id');
        console.log(transactionId);

        $('.btn-update').data('id', transactionId);
    });

    $(".btn-update").on('click', function (e) {
        showLoading();

        e.preventDefault();
        let transactionId = $(this).data('id');
        let foodName = $('#food_name' + transactionId).val();
        let foodTitle = $('#food_title' + transactionId).val();
        let foodSubTitle = $('#food_sub_title' + transactionId).val();
        let price = $('#price' + transactionId).val();
        let oldPrice = $('#old_price' + transactionId).val();
        let category = $('#category' + transactionId).val();
        let isAvailable = $('#is_available' + transactionId).is(':checked');
        let description = editors['description' + transactionId].getData()
        let sizes = [];

        $('.size-selection select[data-food-id="' + transactionId + '"]').each(function () {
            let sizeId = $(this).val();
            let price = $(this).closest('.size-selection').find('input[name="price"]').val();  // Lấy giá từ input
            if (sizeId && price) {
                sizes.push({
                    'size_id': sizeId,
                    'price': price
                });
            }
        });
        let formData = new FormData();
        formData.append('food_name', foodName);
        formData.append('food_title', foodTitle);
        formData.append('food_sub_title', foodSubTitle);
        formData.append('price', price);
        formData.append('old_price', oldPrice);
        formData.append('category', category);
        formData.append('is_available', isAvailable);
        formData.append('description', description);

        sizes.forEach((size, index) => {
            formData.append(`sizes[${index}][size_id]`, size.size_id);
            formData.append(`sizes[${index}][price]`, size.price);
        });

        let imageInput = document.getElementById('imageUploadCover' + transactionId);
        if (imageInput && imageInput.files.length > 0) {
            let file = imageInput.files[0];
            formData.append('image', file);
        } else {
            console.log('No file selected.');
        }
        if (imageInput.files[0]) {
            formData.append('image', imageInput.files[0]);
        }
        for (let [key, value] of formData.entries()) {
            console.log(`${key}:`, value);
        }
        $.ajax({
            url: 'food_item_detail/' + transactionId,
            method: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function (result) {
                alert(result.message, result.alert);
            },
            error: function (response) {
                alert(response.message, response.alert);
            },
            complete: function () {
                demo().then(() => {
                    hideLoading();
                    location.reload();
                });
            }
        });
    });

    $(".delete-link").on('click', function (e) {
        showLoading();
        e.preventDefault();
        let foodId = $(this).data('id');
        Swal.fire({
            title: 'Delete Food Item?',
            text: 'Are you sure you want to delete this food item?',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, delete it!'
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: 'food_item_delete/' + foodId,
                    type: 'DELETE',
                    success: function (result) {
                        alert(result.message, result.alert);
                    },
                    error: function (response) {
                        alert(response.message, response.alert);
                    },
                    complete: function () {
                        demo().then(() => {
                            hideLoading();
                            location.reload();
                        });
                    }
                });
            }
        })
    });

})


function initLightSlider(foodId) {
    var slider = $(`#slider_up${foodId}`).data('lightSlider');

    console.log("slider", slider)
    $('#imageGallery').lightSlider({
        gallery: true,
        item: 1,
        loop: true,
        thumbItem: 9,
        slideMargin: 0,
        enableDrag: false,
        currentPagerPosition: 'left',
        onSliderLoad: function (el) {
            el.lightGallery({
                selector: `#slider_up${foodId} .lslide`,
                download: true,
                zoom: true,
                fullScreen: true,
                share: false,
                thumbnail: true,
                autoplay: false,
                autoplayControls: false,
                actualSize: false,
                counter: false,
            });
        }
    });
}

function readerFunction(input, food_id) {
    var reader = new FileReader();

    reader.onload = function (e) {
        // Xác định các phần tử HTML dựa trên `food_id`
        const previewId = input.id === `imageUpload${food_id}` ? `#imagePreview${food_id}` : `#imagePreviewCover${food_id}`;
        const sliderId = input.id === `imageUpload${food_id}` ? `#slider_up${food_id}` : `#slider_up${food_id}`;

        $(previewId).attr('src', e.target.result);
        $(sliderId).attr('href', e.target.result);

        initLightSlider(food_id);
    };

    reader.readAsDataURL(input.files[0]);
}

function alert(message, alertType) {
    $('#message_alert').html('<div class="message_alert alert alert-' + alertType + ' alert-dismissible fade show show-notification" style="position: fixed" role="alert">' + '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' + '<span aria-hidden="true">&times;</span>' + '</button>' + '<strong>' + message + '</strong>' + '</div>')
}

function showLoading() {
    $("#loading_spinner").removeClass("d-none");
    $("#loadingArea").removeClass("d-none");
}

function hideLoading() {
    $("#loading_spinner").addClass("d-none");
    $("#loadingArea").addClass("d-none");
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function demo() {
    for (let i = 0; i < 3; i++) {
        console.log(`Waiting ${i} seconds...`);
        await sleep(i * 1000);
    }
    console.log('Done');
}
