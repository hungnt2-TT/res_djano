$(document).ready(function () {
    $('.collect-btn').on('click', function (e) {
        e.preventDefault();

        if (!$(this).hasClass('selected')) {
            var couponId = $(this).data('id');
            $(this).text('Collected');
            $(this).addClass('selected');
            $(this).prop('disabled', true);

            $('.collect-btn').not(this).prop('disabled', false).removeClass('selected').text('Collect');
            var subTotal = parseFloat($('#subtotal_all').text());
            var tax = parseFloat($('#tax').text());
            var shipping = parseFloat($('#total_shipping_cost').text());
            var total = parseFloat($('#grand_total').text());
            var total_all = subTotal + tax + shipping;
            $.ajax({
                url: '/marketplace/coupon/collect/',
                type: 'POST',
                data: {
                    'coupon_id': couponId,
                    'subtotal': subTotal,
                    'tax': tax,
                    'shipping': shipping,
                    'total': total_all
                },
                success: function (response) {
                    console.log('Response:', response);
                    if (response['status'] == 'success') {
                        let discountAmount = response.discount.discount || 0;
                        let refundCoin = response.discount.refund_coin || 0;
                        if (refundCoin > 0) {
                            $('#coupon').html(`+ ${refundCoin} Point`);
                            $('#selected_coupon_amount').val(`+ ${refundCoin} Point`);

                        } else {
                            $('#coupon').html(`- ${discountAmount} VND`);
                            $('#selected_coupon_amount').val(`- ${discountAmount} VND`);
                        }
                        $('#grand_total').html(`<em class="dev-menu-grtotal">${response.new_total} VND</em>`);
                        console.log('New Total:', response.new_total);
                        $('#new_total').val(response.new_total);
                        $.ajax({
                            type: 'POST', url: convertToWordsUrl, data: {
                                'amount': response.new_total,
                                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
                            }, success: function (response) {
                                if (response.words) {
                                    $('.total-words span').html(response.words);
                                }
                            }, error: function (response) {
                                console.log('Error:', response);
                            }
                        });
                    } else {
                        Swal.fire({
                            title: 'Error!',
                            text: response.message,
                            icon: 'error',
                            confirmButtonText: 'OK'
                        });
                    }
                }

            });
        }
    });
    $('.menu-order-confirm').on('click', function (e) {
        e.preventDefault();
        var payment_method = $('input[name="payment_method"]:checked').val();

        if (!payment_method) {
            console.log('Please select payment method');
            $('#payment_method-error').html('Please select payment method');
            return false;
        } else {
            Swal.fire({
                title: 'Are you sure to proceed to checkout?',
                text: payment_method + ' as payment method.',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'OK',
                cancelButtonText: 'Cancel'
            }).then((result) => {
                if (result.isConfirmed) {
                    if (payment_method === 'Cash') {
                        $.ajax({
                            url: 'check_phone_verification/',
                            type: 'GET',
                            success: function (response) {
                                if (response.phone_number_verified) {
                                    $('#menu-order-confirm').submit();
                                } else {
                                    Swal.fire({
                                        title: 'Phone Number Not Verified',
                                        text: 'Please verify your phone number before proceeding to checkout.',
                                        icon: 'warning',
                                        confirmButtonText: 'Sure'
                                    }).then((result) => {
                                        if (result.isConfirmed) {
                                            window.location.reload(); // Chuyển hướng đến trang xác minh
                                        }
                                    });
                                }
                            },
                            error: function () {
                                Swal.fire({
                                    title: 'Error',
                                    text: 'An error occurred while checking phone verification status.',
                                    icon: 'error',
                                    confirmButtonText: 'OK'
                                });
                            }
                        });
                    } else if (payment_method === 'Wallet') {
                        var data = parseFloat($('#grand_total').text());

                        $.ajax({
                            url: 'check_wallet_balance/',
                            type: 'GET',
                            data: {
                                'total': data
                            },
                            success: function (response) {
                                ;
                                if (response.status === 'success') {
                                    $('#menu-order-confirm').submit();
                                } else {
                                    Swal.fire({
                                        title: 'Insufficient Balance',
                                        text: 'Your wallet balance is insufficient. Please select another payment method.',
                                        icon: 'warning',
                                        confirmButtonText: 'OK'
                                    });
                                }
                            },
                            error: function () {
                                Swal.fire({
                                    title: 'Error',
                                    text: 'An error occurred while checking wallet balance.',
                                    icon: 'error',
                                    confirmButtonText: 'OK'
                                });
                            }
                        });
                    } else {
                        $('#menu-order-confirm').submit();
                    }
                }
            });
        }
    });
    $('input[name="payment_method"]').on('change', function () {
        $('#payment_method-error').html('');
    });
});