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
    $("#imageUpload, #imageUploadCover").change(function () {
        readerFunction(this);
    });
});

function readerFunction(input) {
    var reader = new FileReader();
    reader.onload = function (e) {
        var previewId = input.id === "imageUpload" ? '#imagePreview' : '#imagePreviewCover';
        var sliderId = input.id === "imageUpload" ? '#slider_up' : '#slider_up_cover';
        $(previewId).attr('src', e.target.result);
        $(sliderId).attr('img_logo', e.target.result);
        initLightSlider();
    }
    console.log("reader", reader)
    reader.readAsDataURL(input.files[0]);
}