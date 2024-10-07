$(document).ready(function () {
    $('input[type="file"][id^="imageUpload"], input[type="file"][id^="imageUploadCover"]').change(function () {
        const food_id = this.id.split('imageUploadCover')[1];
        readerFunction(this, food_id);
    });
    $(".edit-link").on('click', function (e) {
        e.preventDefault();
        let transactionId = $(this).data('id');
        console.log(transactionId);

        $('.btn-update').data('id', transactionId);
    });
    // $(".slider").on('click', function (e) {
    //     e.preventDefault();
    //
    // });
    $(".btn-update").on('click', function (e) {
        e.preventDefault();
        let transactionId = $(this).data('id');

        let data = {
            'food_name': $('.menu-item-title' + transactionId).val(),
            'price': $('.menu-item-price' + transactionId).val(),
            'category': $('#category' + transactionId).val(),
            'image': $('#imageUploadCover' + transactionId).val(),
            'is_available': $('#is_available' + transactionId).is(':checked'),
            'description': $('#description' + transactionId).val(),
        }
        $.ajax({
            url: 'food_edit_detail/' + transactionId,
            type: 'PATCH',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function (result) {
                alert(result.message, result.alert);
                location.reload();
            },
            error: function (response) {
                alert(response.message, response.alert);
            }
        });
    });


})


// $('#menuForm').on('submit', function (e) {
//     e.preventDefault();
//     $.ajax({
//         type: 'POST',
//         url: $('#menuForm').attr('action'),
//         data: new FormData(this),
//         processData: false,
//         contentType: false,
//         success: function (response) {
//             alert(response.message, response.alert);
//             $('#menuForm')[0].reset();
//             $('#message').html('');
//             window.location.reload();
//         },
//
//         error: function (response) {
//             let errors = response.responseJSON.errors;
//             let errorMessages = '<ul>';
//             for (let field in errors) {
//                 errors[field].forEach(function (error) {
//                     errorMessages += error + '<br>';
//                 });
//             }
//             $('#message').html('<div class="text-danger">' + errorMessages + '</div>');
//             alert(response.responseJSON.message, response.responseJSON.alert);
//         }
//     });
// });

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
    const foodId = food_id;
    var reader = new FileReader();
    reader.onload = function (e) {
        var previewId = input.id === `imageUpload${foodId}` ? `#imagePreview${foodId}` : `#imagePreviewCover${foodId}`;
        var sliderId = input.id === `imageUpload${foodId}` ? `#slider_up${foodId}` : `#slider_up${foodId}`;
        console.log("previewId", previewId)
        console.log("sliderId", sliderId)
        $(previewId).attr('src', e.target.result);
        $(sliderId).attr('img_cover', e.target.result);
        initLightSlider(foodId);
    }
    reader.readAsDataURL(input.files[0]);
}

function alert(message, alertType) {
    $('#message_alert').html('<div class="message_alert alert alert-' + alertType + ' alert-dismissible fade show show-notification" style="position: fixed" role="alert">' + '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' + '<span aria-hidden="true">&times;</span>' + '</button>' + '<strong>' + message + '</strong>' + '</div>')
}