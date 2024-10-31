$(document).ready(function () {
    console.log('cart.js loaded');
    $('.change-address-btn').off('click').click(function () {
        var offerSection = $('#offerSection');
        if (offerSection.hasClass('d-none')) {
            offerSection.removeClass('d-none');
        } else {
            offerSection.addClass('d-none');
        }
        console.log('offerSection', !offerSection.hasClass('d-none'));
    });
    $('.item_qty').each(function () {
        var the_id = $(this).attr('id');
        var qty = $(this).attr('data-qty');
        $('#' + the_id).html(qty);
    });

    $('.add_to_cart').off('click').click(function () {
        console.log('clicked');
        var food_id = $(this).attr('data-id');
        var url = $(this).attr('data-url');
        $.ajax({
            type: 'GET', url: url, data: {
                'food_id': food_id
            }, success: function (response) {
                console.log(response);
                if (response.status === 'undefined') {
                    Swal.fire({
                        icon: 'warning',
                        title: 'Not Logged In',
                        text: 'You need to log in to perform this action!',
                        confirmButtonText: 'Log In'
                    }).then((result) => {
                        if (result.isConfirmed) {
                            // Redirect to login page or perform login action
                            window.location.href = '/login';
                        }
                    });
                }
                if (response.quantity !== undefined) {
                    $('#cart_counter').html(response.cart_counter['cart_count']);

                    $('#qty-' + food_id).html(response.quantity);
                    update_price(response.cart_amount.subtotal, response.cart_amount.tax, response.cart_amount.grand_total);

                }
            }, error: function (response) {
                console.log('Error:', response);
            }
        });
        return false;
    });
    $('.decrease_cart').off('click').click(function () {
        var food_id = $(this).attr('data-id');
        var url = $(this).attr('data-url');
        var cart_id = $(this).attr('id')
        $.ajax({
            type: 'GET', url: url, data: {
                'food_id': food_id
            }, success: function (response) {
                console.log('response => ', response);

                if (response.quantity !== undefined) {
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-' + food_id).html(response.quantity);
                    remove_cart(response.quantity, cart_id);
                    update_price(response.cart_amount.subtotal, response.cart_amount.tax, response.cart_amount.grand_total);
                }
            }, error: function (response) {
                console.log('Error:', response);
            }
        });
        return false;
    });
    $('.delete_cart').off('click').click(function () {
        console.log('clicked');
        var cart_id = $(this).attr('data-id');
        var url = $(this).attr('data-url');
        $.ajax({
            type: 'GET', url: url, data: {
                'cart_id': cart_id
            }, success: function (response) {
                console.log(response);
                if (response.status === 'success') {
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    Swal.fire({
                        icon: 'success', title: 'Item Removed', text: 'Item has been removed from cart!',

                    })
                    update_price(response.cart_amount.subtotal, response.cart_amount.tax, response.cart_amount.grand_total);
                    remove_cart(0, cart_id);
                }

            }, error: function (response) {
                console.log('Error:', response);
            }
        });
        return false;
    });

    function remove_cart(cartItemQty, cart_id) {
        if (window.location.pathname === '/marketplace/cart/') {
            if (cartItemQty <= 0) {
                document.getElementById('cart-item-' + cart_id).remove();
            }

            if ($('.menu-itam-list li').length === 0) {
                var marketplaceUrl = $('.menu-itam-list').data('marketplace-url');
                $('.menu-itam-list').html(`
            <div class="text-center p-5" role="alert"
                 style="border: 2px dashed #ccc; border-radius: 10px; background-color: #f9f9f9;">
                <i class="fa fa-shopping-cart fa-3x text-muted mb-3"></i>
                <h3>Your cart is empty</h3>
                <p>Browse our menu and add items to your cart.</p>
                <a href="${marketplaceUrl}" class="btn btn-primary mt-3">Start Shopping</a>
            </div>
        `);
            }
        }
    }

    function update_price(subtotal, tax, grand_total) {
        if (window.location.pathname === '/marketplace/cart/') {
            $('#subtotal_all').html(subtotal);
            $('#tax').html(tax);
            $('#grand_total').html(grand_total);
            $.ajax({
                type: 'POST',
                url: 'convert-to-words/',
                data: {
                    'amount': grand_total,
                    'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
                },

                success: function (response) {
                    console.log(' response is:', response);
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

    $('#sort-by-alphabetical').off('click').click(function (event) {
        event.preventDefault();
        var url = $(this).attr('data-url');
        var action = $(this).attr('data-action');
        console.log('action', action);
        console.log('url', url);
        fetchSortedVendors(action, url);
    });

    function fetchSortedVendors(action, url) {
        const param = updateQueryStringParameter('sort_by', action);
        console.log('param', param);
        $.ajax({
            url: updateQueryStringParameter(window.location.href, 'sort_by', action),
            method: 'GET',
            dataType: 'json',
            success: function (data) {
                console.log('Data:', data.vendors);
                updateVendorList(data.vendors);
            },
            error: function (error) {
                console.error('Error:', error);
            }
        });
    }

    function updateVendorList(vendors) {
        const vendorList = $('.listing.simple ul');
        console.log('vendorList', vendorList);
        vendorList.empty();
        vendors.forEach(vendor => {
            console.log('vendor', vendor);
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

        if (uri.match(re)) {
            return uri.replace(re, '$1' + key + "=" + value + '$2');
        } else {
            return uri + separator + key + "=" + value;
        }
    }
})