$(document).ready(function () {
    const updateOrderUrl = '/update_order/'; // Define the URL

    $('#confirm').click(function () {
        const order_id = $(this).data('id');
        const url = `${updateOrderUrl}${order_id}/`; // Construct the URL with the order ID

        $.ajax({
            url: url,
            type: 'POST',
            data: {
                'status': 'confirmed'
            },
            success: function(response) {
                // Handle success
                console.log('Order updated successfully:', response);
            },
            error: function(error) {
                // Handle error
                console.error('Error updating order:', error);
            }
        });
    });
});