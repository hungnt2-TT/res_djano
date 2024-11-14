$(document).ready(function () {
    $('.accept-btn').click(function () {
        var orderId = $(this).closest('.order-card').data('order-id');
        var url = $(this).data('url');
        handleOrderAction(orderId, url, 'accept');
    });

    $('.reject-btn').click(function () {
        var orderId = $(this).closest('.order-card').data('order-id');
        var url = $(this).data('url');
        handleOrderAction(orderId, url, 'reject');
    });

    function handleOrderAction(orderId, url, action) {
        $.ajax({
            url: url.replace('order_id', orderId),
            type: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            },
            success: function (response) {
                console.log(response);
                if (response.status === 'success') {
                    Swal.fire({
                        icon: 'success',
                        title: 'Success',
                        text: 'Order has been ' + action + 'ed successfully.'
                    });
                    $('[data-order-id="' + orderId + '"]').remove();
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: response.message
                    });
                }
            },
            error: function () {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Something went wrong. Please try again later.'
                });
            }
        });
    }
});
