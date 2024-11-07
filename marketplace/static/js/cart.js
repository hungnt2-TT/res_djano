$(document).ready(function () {
    console.log('cart.js loaded');
    let shopTotals = {};

    function updateTotalDisplay(shopId) {
        $(`#currency_id${shopId}`).text(shopTotals[shopId] + ' VND');
        let totalAllShops = Object.values(shopTotals).reduce((acc, total) => acc + total, 0);
        $('#total').text(totalAllShops + ' VND');
    }

    function updatePrice(subtotal, tax, grandTotal, shipping = 0, type = '') {
        console.log('shipping:', shipping);
        if (window.location.pathname === '/marketplace/cart/') {
            const $totalShippingCostElement = $("#total_shipping_cost");
            $totalShippingCostElement.text(shipping + ' VND');
            $('#subtotal_all').html(subtotal + ' VND');
            $('#tax').html(tax + ' VND');
            if (type === 'add') {
                $('#grand_total').html(grandTotal + shipping + ' VND');
            } else {
                $('#grand_total').html(grandTotal + ' VND');
            }
            $.ajax({
                type: 'POST', url: 'convert-to-words/', data: {
                    'amount': grandTotal, 'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
                }, success: function (response) {
                    if (response.words) {
                        $('.total-words span').html(response.words);
                    }
                }, error: function (response) {
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
            console.log('response:', response);
            const $totalShippingCostElement = $("#total_shipping_cost");
            let currentTotalShippingCost = parseFloat($totalShippingCostElement.text().replace(' VND', '').trim());
            let newTotalShippingCost = shipCost;
            updatePrice(response.cart_amount.subtotal, response.cart_amount.tax, response.cart_amount.grand_total, shipCost, type = 'add');
            shopTotals[shopId] += itemPrice;
            updateTotalDisplay(shopId);
        }
    }

    function handleDeleteCartSuccess(response, shopId, itemPrice, cartItemId, vendorElement, quantity) {
        if (response.status === 'success') {
            shopTotals[shopId] -= itemPrice;
            updateTotalDisplay(shopId);

            setTimeout(function () {
                $(`.cart-item[data-item-id="${cartItemId}"]`).remove();
                if (vendorElement.find('.cart-item').length === 0) {
                    vendorElement.remove();
                    console.log('quantity:', quantity);
                    console.log('cartItemId:', cartItemId);
                    const newGrandTotal = response.cart_amount.grand_total - itemPrice * quantity;
                    const newSubtotal = response.cart_amount.subtotal - itemPrice * quantity;
                    $('#subtotal_all').html(newSubtotal + ' VND');
                    $('#grand_total').html(newGrandTotal + ' VND');
                    if (quantity === 0) {
                        $(`.cart-item[data-item-id="${cartItemId}"]`).remove();
                        if (vendorElement.find('.cart-item').length === 0) {
                            vendorElement.remove();
                        }
                        removeCart();
                    }
                    console.log('response.cart_amount.ship_cost:', response.cart_amount.ship_cost);
                    const $totalShippingCostElement = $("#total_shipping_cost");
                    let currentTotalShippingCost = parseFloat($totalShippingCostElement.text().replace(' VND', '').trim());
                    let newTotalShippingCost = currentTotalShippingCost - response.cart_amount.ship_cost;
                    updatePrice(newSubtotal, response.cart_amount.tax, newGrandTotal, newTotalShippingCost);
                }
                removeCart();
            }, 500);
        }
    }

    function handleDecreaseCartSuccess(response, shopId, itemPrice, cartItemId, vendorElement, foodId) {
        if (response.quantity !== undefined) {

            console.log('response:', response);
            $('#qty-' + foodId).html(response.quantity);

            $('#cart_counter').html(response.cart_counter['cart_count']);
            updatePrice(response.cart_amount.subtotal, response.cart_amount.tax, response.cart_amount.grand_total);
            shopTotals[shopId] -= itemPrice;
            updateTotalDisplay(shopId);
            console.log('response.quantity:', response);
            updatePrice(response.cart_amount.subtotal, response.cart_amount.tax, response.cart_amount.grand_total, response.cart_amount.ship_cost);
            if (response.quantity === 0) {
                $(`.cart-item[data-item-id="${cartItemId}"]`).remove();
                if (vendorElement.find('.cart-item').length === 0) {
                    vendorElement.remove();
                }
                removeCart(response.cart_counter['cart_count'], foodId, sizeId, shipCost);
            }
        }
    }

    function fetchSortedVendors(action, url) {
        $.ajax({
            url: updateQueryStringParameter(window.location.href, 'sort_by', action),
            method: 'GET',
            dataType: 'json',
            success: function (data) {
                updateVendorList(data.vendors);
            },
            error: handleAjaxError
        });
    }

    function updateVendorList(vendors) {
        const vendorList = $('.listing.simple ul');
        vendorList.empty();
        vendors.forEach(vendor => {
            const vendorItem = `
            <li>
                <div class="img-holder">
                    <figure>
                        <a href="#"><img src="${vendor.profile_picture}" class="img-list wp-post-image" alt=""></a>
                    </figure>
                    <span class="restaurant-status close"><em class="bookmarkRibbon"></em>Close</span>
                </div>
                <div class="text-holder">
                    <div class="list-rating">
                        <div class="rating-star">
                            <span class="rating-box" style="width: 100%;"></span>
                        </div>
                        <span class="reviews">(1)</span>
                    </div>
                    <div class="post-title">
                        <h5>
                            <a href="/vendor/${vendor.vendor_slug}">${vendor.vendor_name}</a>
                            <span class="sponsored text-color">Sponsored</span>
                        </h5>
                    </div>
                    <address>
                        <span>Address:</span>${vendor.address_line_1}
                        <br>
                        <a href="https://www.google.com/maps?q=${vendor.address_line_1}" target="_blank">Xem trên Google Maps</a>
                    </address>
                    <div class="delivery-potions">
                        <div class="post-time">
                            <i class="icon-motorcycle"></i>
                            <div class="time-tooltip">
                                <div class="time-tooltip-holder"><b class="tooltip-label">Delivery time</b> <b class="tooltip-info">Your order will be delivered in 10 minutes.</b></div>
                            </div>
                        </div>
                        <div class="post-time">
                            <i class="icon-clock4"></i>
                            <div class="time-tooltip">
                                <div class="time-tooltip-holder"><b class="tooltip-label">Pickup time</b> <b class="tooltip-info">You can pickup order in 15 minutes.</b></div>
                            </div>
                            <span>Totnes, Devon</span>
                        </div>
                        <span><small><b>Distance: ${vendor.kms} km</b> away from ${vendor.address}</small></span>
                    </div>
                    <div class="list-option">
                        <a href="javascript:void(0);" class="shortlist-btn" data-toggle="modal" data-target="#sign-in"><i class="icon-heart4"></i> </a>
                        <a href="/vendor/${vendor.vendor_slug}" class="viewmenu-btn text-color">View Menu</a>
                    </div>
                </li>
            `;
            vendorList.append(vendorItem);
        });
    }

    function updateQueryStringParameter(uri, key, value) {
        var re = new RegExp("([?&])" + key + "=.*?(&|$)", "i");
        var separator = uri.indexOf('?') !== -1 ? "&" : "?";
        return uri.match(re) ? uri.replace(re, '$1' + key + "=" + value + '$2') : uri + separator + key + "=" + value;
    }

    function showLoading() {
        $("#loading_spinner").removeClass("d-none");
        $("#loadingArea").removeClass("d-none");
    }

    function hideLoading() {
        $("#loading_spinner").addClass("d-none");
        $("#loadingArea").addClass("d-none");
    }

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

    $('.change-address-btn').off('click').click(function () {
        var offerSection = $('#offerSection');
        offerSection.toggleClass('d-none');
    });

    $('.item_qty').each(function () {
        var the_id = $(this).attr('id');
        var qty = $(this).attr('data-qty');
        $('#' + the_id).html(qty);
    });

    $('.add_to_cart').off('click').click(function () {
        const vendorId = $(this).closest('.list-cart-item').data('vendor-id');
        const vendorElement = $(`.list-cart-item[data-vendor-id="${vendorId}"]`);
        const shopId = $(this).data('shop-id').split('_')[0];
        const foodId = $(this).attr('data-id');
        const url = $(this).attr('data-url');
        const sizeId = $('#size_option_' + foodId).attr('data-size-id');
        const itemPrice = parseFloat($(this).closest('.cart-item').find('.price').text().replace(' VND', ''));
        const shipCost = parseFloat(vendorElement.find('#shipping').text()) || 0;
        console.log('shipCost:', shipCost);
        if (!shopTotals[shopId]) {
            shopTotals[shopId] = 0;
        }

        $.ajax({
            type: 'POST', url: url, data: {
                'food_id': foodId, 'sizeId': sizeId, 'firstSizeId': sizeId
            }, success: function (response) {
                handleAddToCartSuccess(response, shopId, itemPrice, foodId, shipCost);
            }, error: handleAjaxError
        });
        return false;
    });

    $('.delete_cart').off('click').click(function (e) {
        e.preventDefault();

        showLoading();
        const cartItemId = $(this).data('item-id');
        const vendorId = $(this).closest('.list-cart-item').data('vendor-id');
        const vendorElement = $(`.list-cart-item[data-vendor-id="${vendorId}"]`);
        const shopId = $(this).data('shop-id');
        const itemPrice = parseFloat($(this).closest('.cart-item').find('.price').text().replace(' VND', ''));
        const foodId = $(this).attr('data-id');
        const sizeId = $(this).attr('data-size-id');
        const url = $(this).attr('data-url');
        const quantityID = $(this).attr('data-quan');
        const shipCost = parseFloat(vendorElement.find('#shipping').text()) || 0;

        // Use the `quantityID` to get the quantity label
        const quantity = $(`#qty-${quantityID}`).text();
        $.ajax({
            type: 'POST', url: url, data: {
                'food_id': foodId, 'firstSizeId': sizeId, 'shipCost': shipCost
            }, success: function (response) {
                handleDeleteCartSuccess(response, shopId, itemPrice, cartItemId, vendorElement, quantity);
                hideLoading();
            },

            error: handleAjaxError
        });
        return false;
    });

    $('.decrease_cart').off('click').click(function () {
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
            type: 'POST', url: url, data: {
                'food_id': foodId, 'firstSizeId': sizeId, 'shipCost': shipCost
            }, success: function (response) {
                handleDecreaseCartSuccess(response, shopId, itemPrice, cartItemId, vendorElement, foodId);
            }, error: handleAjaxError
        });
        return false;
    });

    $('#sort-by-alphabetical').off('click').click(function (event) {
        event.preventDefault();
        var url = $(this).attr('data-url');
        var action = $(this).attr('data-action');
        fetchSortedVendors(action, url);
    });
});