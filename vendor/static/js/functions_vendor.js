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
function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        console.log('readURL')
        reader.onload = function (e) {
            $('#imagePreview').attr('src', e.target.result);
        }
        reader.readAsDataURL(input.files[0]);
    }
}

$(document).ready(function () {
    $("#imageUpload").change(function () {
        console.log('change')
        readURL(this);
    });
    $("#imagePreview").click(function () {
        console.log('click')
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
                    selector: '#imageGallery .lslide',
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

    $(".toggle-password").click(function () {
        $(this).toggleClass("fa-eye fa-eye-slash");
        var input = $($(this).attr("toggle"));
        if (input.attr("type") == "password") {
            input.attr("type", "text");
        } else {
            input.attr("type", "password");
        }
    });
});