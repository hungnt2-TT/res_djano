document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM loaded');

    const form = document.getElementById('order-form');
    const url = form.getAttribute('data-url');
    console.log('url:', url);
    form.addEventListener('submit', function (e) {
        showLoading();
        e.preventDefault();

        const formData = new FormData(form);

        const orderDetailsElement = document.getElementById('order-details-data');
        let orderDetails;

        try {
            const jsonContent = orderDetailsElement.textContent.trim();
            console.log('JSON Content:', jsonContent);  // Kiểm tra lại nội dung JSON lấy được
            orderDetails = JSON.parse(jsonContent);
        } catch (e) {
            alert("Có lỗi xảy ra khi xử lý dữ liệu đơn hàng. Vui lòng thử lại.");
            hideLoading();
            return;  // Nếu có lỗi, ngừng thực hiện
        }

        formData.append('order_details', JSON.stringify(orderDetails));

        console.log('Form data:', formData);
        fetch('/orders/place-order/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            }
        })
            .then(response => response.json())
            .then(data =>   {
                if (data.status === 'success') {
                    const orderDetails = data.order;
                    console.log('Order placed successfully:', data);
                    if (orderDetails.payment_method == 3) {
                        // Redirect to PayPal payment page
                        window.location.href = data.redirect_url;
                        return;
                    }
                    else if (orderDetails.payment_method == 1) {
                        // Redirect to Stripe payment page
                        window.location.href = data.vn_pay_url;
                        return;
                    }
                    Swal.fire({
                        title: 'Order Placed Successfully!',
                        text: 'Your order has been placed successfully. Order number: ' + orderDetails.order_number,
                        icon: 'success',
                        confirmButtonText: 'OK'
                    })
                    // Redirect to order confirmation page
                    // window.location.href = data.success_url
                    window.location.href = data.order_detail
                } else {
                    Swal.fire({
                        title: 'Error!',
                        text: data.message,
                        icon: 'error',
                        confirmButtonText: 'OK'
                    });
                    window.location.href = data.failed_url;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while processing your order. Please try again.');
            })
            .finally(() => {
                hideLoading();
            });

        function hideLoading() {
            document.getElementById('loading_spinner').style.display = 'none';
            document.getElementById('loadingArea').style.display = 'none';

        }

        function showLoading() {
            console.log('Loading...');
            document.getElementById('loading_spinner').classList.remove('d-none');
            document.getElementById('loadingArea').classList.remove('d-none');
        }
    });
});

