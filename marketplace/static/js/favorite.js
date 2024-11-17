$(document).ready(function () {
    console.log('Favorite script loaded');
    $('.shortlist-btn').each(function () {
        console.log('Shortlist button found');
        $(this).on('click', function () {
            console.log('Shortlist button clicked');
            const btn = $(this);
            const vendorId = btn.data('id');
            const favorited = btn.data('favorited') === true;
            const url = $(this).data('url');
            console.log('Vendor ID:', vendorId);
            console.log('Favorited:', favorited);
            console.log('URL:', url);
            $.ajax({
                url: url,
                type: 'POST',
                headers: {
                    'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
                },
                success: function (data) {
                    console.log('Success:', data);
                    if (data.status === 'added') {
                        btn.find('i').addClass('favorited');
                        btn.data('favorited', true);
                    } else if (data.status === 'removed') {
                        console.log('Removed');
                        btn.find('i').removeClass('favorited');
                        btn.data('favorited', false);
                    }
                },
                error: function (error) {
                    console.error('Error:', error);
                }
            });
        });
    });
});