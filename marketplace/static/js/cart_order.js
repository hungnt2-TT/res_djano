$(document).ready(function () {
    let selectedSizePrice = 0;
    let quantity = 1;
    let firstSizeId = 0;

    const firstSize = $('input[name="size_option"]').last();
    console.log('First size:', firstSize);
    if (firstSize.length > 0) {
        firstSizeId = firstSize.val();
        console.log('First size ID:', firstSizeId);
        selectedSizePrice = sizes[firstSizeId].price;
        firstSize.prop('checked', true);
        $('#price-display').text(selectedSizePrice + ' VND');
        updateTotalPrice(quantity);
    }

    $('input[type="radio"][name="size_option"]').off('click').click(function () {
        firstSizeId = $(this).val();
        console.log('Size ID:', firstSizeId);
        // Lấy giá trị price từ sizes dựa trên sizeId
        if (sizes[firstSizeId]) {
            selectedSizePrice = sizes[firstSizeId].price;
            $('#price-display').text(selectedSizePrice + ' VND');
            // Cập nhật giá dựa trên số lượng hiện tại
            updateTotalPrice(quantity);
        }
    });

    $('.add_to_cart').off('click').on('click', function () {
        const foodId = $(this).data('id');
        const quantityLabel = $('#qty-' + foodId);
        quantity = parseInt(quantityLabel.text());
        quantity += 1;
        quantityLabel.text(quantity);

        updateTotalPrice(quantity);
    });

    $('.decrease_cart').off('click').on('click', function () {
        const foodId = $(this).data('id');
        const quantityLabel = $('#qty-' + foodId);
        quantity = parseInt(quantityLabel.text());

        if (quantity > 0) {
            quantity -= 1;
            quantityLabel.text(quantity);
            updateTotalPrice(quantity);
        }
    });

    function updateTotalPrice(quantity) {
        console.log(selectedSizePrice, quantity);
        const totalPrice = selectedSizePrice * quantity;
        $('#price-display').text(totalPrice + ' VND');
    }

    $('#add_to_cart').off('click').on('click', function () {
        var url = $(this).attr('data-url');
        const foodId = $(this).data('id');
        console.log('Add to cart:', foodId);
        const sizeId = $('#size_option_' + foodId).val();
        quantity = parseInt(quantity) || 1;
        const note = $('#note_' + foodId).val();

        // Lấy giá size dựa trên option đã chọn
        const sizePrice = selectedSizePrice;
        console.log('sizePrice ID:', sizePrice);
        console.log('Size price:', sizePrice);
        console.log('Size ID:', firstSizeId, 'Quantity:', quantity, 'Note:', note);
        $.ajax({
            url: url,
            method: 'POST',
            data: {
                food_id: foodId,
                size_id: sizeId,
                firstSizeId: firstSizeId,
                quantity: quantity,
                note: note,
                size_price: sizePrice,
                csrfmiddlewaretoken: '{{ csrf_token }}'
            },
            success: function (response) {
                console.log(response);
                if (response.status === 'undefined') {
                    Swal.fire({
                        icon: 'warning',
                        title: 'Not Logged In',
                        text: 'You need to log in to perform this action!',
                        confirmButtonText: 'Log In'
                    }).then((result) => {
                        if (result.isConfirmed) {
                            window.location.href = '/login';
                        }
                    });
                }
                if (response.quantity !== undefined) {
                    $('#cart_counter').html(response.cart_counter['cart_count']);


                }
            }, error: function (response) {
                console.log('Error:', response);
            }
        });
    })
});
