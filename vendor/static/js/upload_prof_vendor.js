function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            $('#imagePreview').attr('src', e.target.result);
            $('#slider_up').attr('img_logo', e.target.result);

            initLightSlider();
        }
        console.log("reader", reader)
        reader.readAsDataURL(input.files[0]);
    }
}

function initLightSlider() {
    var slider = $('#slider_up').data('lightSlider')
    console.log("slider", slider)
    // if (slider) {
    //     slider.destroy();
    // }
    $('#imageGallery').removeData('lightSlider');
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
                selector: '#slider_up .lslide',
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

$(document).ready(function () {
    $("#imageUpload").change(function () {
        readURL(this);
    });
});