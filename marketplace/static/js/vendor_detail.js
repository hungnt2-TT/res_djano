/*
$(document).ready(function () {
    $('#booking-form').on('submit', function (e) {
        e.preventDefault();
        const form = $(this);
        const url = form.attr('action');
        console.log(url);
        const data = form.serialize();
        $.ajax({
            url: url,
            type: 'POST',
            data: data,
            success: function (response) {
                if (response['status'] === 'error') {
                    alert(response['message']);
                } else {
                    alert('予約が完了しました。');
                    location.reload();
                }
            },
            error: function (response) {
                alert('予約に失敗しました。');
            }
        })
    })
})*/
