$(document).ready(function () {
    console.log('My Orders page loaded');
    // Khởi tạo Date Range Picker
    $('#dateRange').daterangepicker({
        opens: 'left', // Mở calendar bên trái
        locale: {
            format: 'YYYY-MM-DD', // Định dạng ngày tháng
            applyLabel: 'Áp dụng',
            cancelLabel: 'Hủy'
        }
    });

    // Xử lý khi người dùng chọn khoảng thời gian và nhấn tìm kiếm
    $('#searchForm').on('submit', function (e) {
        e.preventDefault();  // Ngừng hành động mặc định của form

        const dateRange = $('#dateRange').val(); // Lấy giá trị date range đã chọn
        console.log('Khoảng thời gian:', dateRange);  // In ra khoảng thời gian người dùng đã chọn

        // Xử lý logic tìm kiếm ở đây, ví dụ: gửi yêu cầu AJAX với date range
        searchProducts(dateRange);
    });
});
