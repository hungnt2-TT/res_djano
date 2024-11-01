// $(document).ready(function () {
//     $('#imageGallery').lightSlider({
//         gallery: true,
//         item: 1,
//         loop: true,
//         thumbItem: 9,
//         slideMargin: 0,
//         enableDrag: false,
//         currentPagerPosition: 'left',
//         onSliderLoad: function (el) {
//             el.lightGallery({
//                 selector: '#imageGallery .lslide'
//             });
//         }
//     })
// })


$(document).ready(function () {
    console.log('Document ready');
    $(document).on('change', '.image-upload', function () {
        console.log('Image changed');
        var previewId = $(this).data('preview-id');
        console.log('previewId', previewId);
        // Pass preview ID dynamically
        if (typeof readURL === 'function') {
            readURL(this, previewId); // Pass preview ID dynamically
        } else {
            console.error('readURL function is not defined');
        }
    });
    $(document).on('click', '.thumbnail', function () {
        console.log('Thumbnail clicked');
        var galleryId = $(this).closest('.foodbakery-gallery-holder').data('gallery-id');
        console.log('galleryId', galleryId);
        $('#' + galleryId).lightSlider({
            gallery: true,
            item: 1,
            loop: true,
            thumbItem: 9,
            slideMargin: 0,
            enableDrag: false,
            currentPagerPosition: 'left',
            onSliderLoad: function (el) {
                el.lightGallery({
                    selector: '#' + galleryId + ' .lslide',
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
    });

    $(document).on('click', '.toggle-password', function () {
        var input = $($(this).attr("toggle"));
        if (input.attr("type") == "password") {
            input.attr("type", "text");
        } else {
            input.attr("type", "password");
        }
    });
});

function readURL(input, previewId) {
    console.log('Reading URL', previewId);
    if (input.files && input.files[0]) {
        console.log('Reading URL');
        var reader = new FileReader();
        console.log('reader', reader);

        reader.onload = function (e) {
            $('#' + previewId).attr('src', e.target.result);
        };
        console.log('reader', input.files[0])
        reader.readAsDataURL(input.files[0]);
    }
}

function resadURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        console.log('readURL')
        reader.onload = function (e) {
            $('#imagePreview').attr('src', e.target.result);
        }
        reader.readAsDataURL(input.files[0]);
    }
}