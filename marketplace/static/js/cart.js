$(document).ready(function () {
    let shopTotals = {};

    // Initialize shop totals
    $('.total-item-by-store').each(function () {
        const shopId = $(this).data('shop-id');
        const total = parseFloat($(this).find('.currency').text()) || 0;
        shopTotals[shopId] = total;
    });

    $('.shipping_cost').each(function () {
        const shopId = $(this).data('shop-id');
        const shippingFee = parseFloat($(this).find('#shipping').text()) || 0;
        shopTotals[shopId] += shippingFee;
    });

    // Utility functions
    function updateTotalDisplay(shopId, itemPrice = 0) {
        console.log('Updating total for shopId:', shopId, 'New total:', shopTotals[shopId]);
        $(`#currency_id${shopId}`).text(shopTotals[shopId] + ' VND');
        console.log('Total all shops:', itemPrice);
        $('#total').text(itemPrice + ' VND');
    }

    function updatePrice(subtotal, tax, grandTotal, shipping = 0, type = '') {
        console.log('shipping:', shipping);
        if (window.location.pathname === '/marketplace/cart/') {
            const totalShippingCostElement = parseInt($("#total_shipping_cost").text().replace(' VND', '').trim(), 10);

            $('#subtotal_all').html(subtotal + ' VND');
            $('#tax').html(tax + ' VND');
            if (type === 'add' || type === 'decrease') {
                $('#grand_total').html(grandTotal + totalShippingCostElement + ' VND');
            } else {
                const $totalShippingCostElement = $("#total_shipping_cost");
                var newTotalShippingCost = totalShippingCostElement - shipping;
                $totalShippingCostElement.text(newTotalShippingCost + ' VND');
                $('#grand_total').html(grandTotal + newTotalShippingCost + ' VND');
            }
            $.ajax({
                type: 'POST',
                url: 'convert-to-words/',
                data: {
                    'amount': grandTotal + totalShippingCostElement,
                    'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
                },
                success: function (response) {
                    if (response.words) {
                        $('.total-words span').html(response.words);
                    }
                },
                error: function (response) {
                    console.log('Error:', response);
                }
            });
        }
    }

    function removeCart() {
        if (window.location.pathname === '/marketplace/cart/') {
            if ($('.menu-itam-list li').length === 0) {
                $('#subtotal_all').html('0 VND');
                $('#tax').html('0 VND');
                $('#grand_total').html('0 VND');
                $('#total_shipping_cost').html('0 VND');
                $('.total-words span').html('...');
                const marketplaceUrl = $('.menu-itam-list').data('marketplace-url');
                $('.menu-itam-list').html(`
                    <div class="text-center p-5" role="alert" style="border: 2px dashed #ccc; border-radius: 10px; background-color: #f9f9f9;">
                        <i class="fa fa-shopping-cart fa-3x text-muted mb-3"></i>
                        <h3>Your cart is empty</h3>
                        <p>Browse our menu and add items to your cart.</p>
                        <a href="${marketplaceUrl}" class="btn btn-primary mt-3">Start Shopping</a>
                    </div>
                `);
            }
        }
    }

    function handleAjaxError(response) {
        console.log('Error:', response);
    }

    function handleAddToCartSuccess(response, shopId, itemPrice, foodId, shipCost) {
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
            $('#qty-' + foodId).html(response.quantity);
            updatePrice(response.cart_amount.subtotal, response.cart_amount.tax, response.cart_amount.grand_total, shipCost, type = 'add');
            shopTotals[shopId] += itemPrice;
            updateTotalDisplay(shopId, itemPrice * response.quantity);
        }
    }

    function handleDeleteCartSuccess(response, shopId, itemPrice, cartItemId, vendorElement, quantity) {
        if (response.status === 'success') {
            shopTotals[shopId] -= itemPrice * quantity;
            updateTotalDisplay(shopId);

            // Xóa mục khỏi giao diện người dùng
            $(`.cart-item[data-item-id="${cartItemId}"]`).remove();

            // Kiểm tra xem cửa hàng còn sản phẩm nào không
            if (vendorElement.find('.cart-item').length === 0) {
                vendorElement.remove();
            }

            // Cập nhật tổng giá cho toàn bộ giỏ hàng
            const newGrandTotal = response.cart_amount.grand_total;
            const newSubtotal = response.cart_amount.subtotal;
            const newTax = response.cart_amount.tax;
            const newShippingCost = response.cart_amount.total_shipping_cost;

            $('#subtotal_all').html(newSubtotal + ' VND');
            $('#tax').html(newTax + ' VND');
            $('#total_shipping_cost').html(newShippingCost + ' VND');
            $('#grand_total').html(newGrandTotal + ' VND');

            // Cập nhật tổng số lượng sản phẩm trong giỏ hàng
            $('#cart_counter').html(response.cart_counter['cart_count']);

            // Kiểm tra nếu giỏ hàng trống
            if (response.cart_counter['cart_count'] === 0) {
                removeCart();
            }
        }
    }

    function handleDecreaseCartSuccess(response, shopId, itemPrice, cartItemId, vendorElement, foodId) {
        console.log('response:', response, 'shopId:', shopId, 'itemPrice:', itemPrice, 'cartItemId:', cartItemId, 'vendorElement:', vendorElement, 'foodId:', foodId);
        if (response.quantity !== undefined) {
            $('#qty-' + foodId).html(response.quantity);
            $('#cart_counter').html(response.cart_counter['cart_count']);
            shopTotals[shopId] -= itemPrice;
            updateTotalDisplay(shopId, response.cart_amount.subtotal);
            updatePrice(response.cart_amount.subtotal, response.cart_amount.tax, response.cart_amount.grand_total, response.cart_amount.ship_cost, 'decrease');
            if (response.quantity === 0) {
                $(`.cart-item[data-item-id="${cartItemId}"]`).remove();
                if (vendorElement.find('.cart-item').length === 0) {
                    vendorElement.remove();
                    removeCart();
                }
            }
        }
    }

    function showLoading() {
        $("#loading_spinner").removeClass("d-none");
        $("#loadingArea").removeClass("d-none");
    }

    function hideLoading() {
        $("#loading_spinner").addClass("d-none");
        $("#loadingArea").addClass("d-none");
    }

    // Event handlers
    $('#checkout-cart').click(function (event) {
        event.preventDefault();
        const vendorItems = $('.list-cart-item');
        const vendorCount = vendorItems.length;

        if (vendorCount > 1) {
            const message = `You have items from ${vendorCount} vendors in your cart. This may increase the delivery fee and time. Do you want to proceed?`;
            Swal.fire({
                title: 'Confirm Checkout',
                text: message,
                icon: 'warning',
                showCancelButton: true,
            }).then((result) => {
                if (result.isConfirmed) {
                    $('#checkout').submit();
                }
            });
        } else if (vendorCount === 1) {
            $('#checkout').submit();
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Empty Cart',
                text: 'Your cart is empty. Please add items to your cart to proceed.'
            });
        }
    });

    $('.change-address-btn').click(function () {
        var offerSection = $('#offerSection');
        offerSection.toggleClass('d-none');
    });

    $('.add_to_cart').click(function () {
        const vendorId = $(this).closest('.list-cart-item').data('vendor-id');
        const vendorElement = $(`.list-cart-item[data-vendor-id="${vendorId}"]`);
        const shopId = $(this).data('shop-id').split('_')[0];
        const foodId = $(this).attr('data-id');
        const url = $(this).attr('data-url');
        const sizeId = $('#size_option_' + foodId).attr('data-size-id');
        const itemPrice = parseFloat($(this).closest('.cart-item').find('.price').text().replace(' VND', ''));
        const shipCost = parseFloat(vendorElement.find('#shipping').text()) || 0;

        if (!shopTotals[shopId]) {
            shopTotals[shopId] = 0;
        }

        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'food_id': foodId,
                'sizeId': sizeId,
                'firstSizeId': sizeId
            },
            success: function (response) {
                handleAddToCartSuccess(response, shopId, itemPrice, foodId, shipCost);
            },
            error: handleAjaxError
        });
        return false;
    });

    $('.delete_cart').click(function (e) {
        e.preventDefault();
        showLoading();
        const cartItemId = $(this).data('item-id');
        const vendorId = $(this).closest('.list-cart-item').data('vendor-id');
        const vendorElement = $(`.list-cart-item[data-vendor-id="${vendorId}"]`);
        const shopId = $(this).data('shop-id');
        const itemPrice = parseFloat($(this).closest('.cart-item').find('.price').text().replace(' VND', ''));
        console.log('itemPrice:', itemPrice);
        const foodId = $(this).attr('data-id');
        const sizeId = $(this).attr('data-size-id');
        console.log('sizeId:', sizeId);
        const url = $(this).attr('data-url');
        const quantityID = $(this).attr('data-quan');
        const shipCost = parseFloat(vendorElement.find('#shipping').text()) || 0;
        const quantity = parseInt($(`#qty-${quantityID}`).text(), 10);
        console.log('quantity:', quantity);
        console.log('shopId:', shopId);
        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'food_id': foodId,
                'firstSizeId': sizeId,
                'shipCost': shipCost,
                'quantity': quantity
            },
            success: function (response) {
                if (response.status === 'success') {
                    console.log('response:', response);
                    // Cập nhật tổng giá cho cửa hàng cụ thể
                    shopTotals[shopId] -= itemPrice * quantity;
                    updateTotalDisplay(shopId, response.cart_amount.subtotal);

                    // Xóa mục khỏi giao diện người dùng
                    $(`.cart-item[data-item-id="${cartItemId}"]`).remove();

                    // Kiểm tra xem cửa hàng còn sản phẩm nào không
                    if (vendorElement.find('.cart-item').length === 0) {
                        vendorElement.remove();
                    }

                    // Cập nhật tổng giá cho toàn bộ giỏ hàng
                    const currentGrandTotal = parseFloat($('#grand_total').text().replace(' VND', ''));
                    const newGrandTotal = Math.max(0, response.cart_amount.grand_total);
                    const currentSubtotal = parseFloat($('#subtotal_all').text().replace(' VND', ''));
                    const newSubtotal = Math.max(0, currentSubtotal - (itemPrice * quantity));

                    $('#subtotal_all').html(newSubtotal + ' VND');
                    $('#grand_total').html(newGrandTotal + ' VND');

                    // Cập nhật tổng số lượng sản phẩm trong giỏ hàng
                    const newCartCount = parseInt($('#cart_counter').text()) - quantity;
                    $('#cart_counter').html(newCartCount);

                    // Kiểm tra nếu giỏ hàng trống
                    if (newCartCount === 0) {
                        removeCart();
                    }

                    // Cập nhật tổng phí vận chuyển
                    const currentShippingCost = parseFloat($('#total_shipping_cost').text().replace(' VND', ''));
                    const newShippingCost = vendorElement.find('.cart-item').length === 0 ?
                        Math.max(0, currentShippingCost - shipCost) : currentShippingCost;
                    $('#total_shipping_cost').html(newShippingCost + ' VND');

                    updateTotalWords(newGrandTotal);
                }
                hideLoading();
            },
            error: handleAjaxError
        });
        return false;
    });
    $('.decrease_cart').click(function () {
        const cartItemId = $(this).data('item-id');
        const vendorId = $(this).closest('.list-cart-item').data('vendor-id');
        const vendorElement = $(`.list-cart-item[data-vendor-id="${vendorId}"]`);
        const shopId = $(this).data('shop-id').split('_')[0];
        const foodId = $(this).attr('data-id');
        const sizeId = $(this).attr('data-size-id');
        const url = $(this).attr('data-url');
        const itemPrice = parseFloat($(this).closest('.cart-item').find('.price').text().replace(' VND', ''));
        const shipCost = parseFloat(vendorElement.find('#shipping').text()) || 0;

        if (!shopTotals[shopId]) {
            shopTotals[shopId] = 0;
        }

        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'food_id': foodId,
                'firstSizeId': sizeId,
                'shipCost': shipCost
            },
            success: function (response) {
                handleDecreaseCartSuccess(response, shopId, itemPrice, cartItemId, vendorElement, foodId);
            },
            error: handleAjaxError
        });
        return false;
    });

    function updateTotalWords(amount) {
        $.ajax({
            type: 'POST',
            url: 'convert-to-words/',
            data: {
                'amount': amount,
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function (response) {
                if (response.words) {
                    $('.total-words span').html(response.words);
                }
            },
            error: function (response) {
                console.log('Error:', response);
            }
        });
    }

    $('#sort-by-alphabetical').off('click').click(function (event) {
        event.preventDefault();
        var url = $(this).attr('data-url');
        var action = $(this).attr('data-action');
        fetchSortedVendors(action, url);
    });
});

