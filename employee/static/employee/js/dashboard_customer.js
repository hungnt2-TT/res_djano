// document.addEventListener('DOMContentLoaded', function() {
//     // Kiểm tra xem Chart.js đã được tải chưa
//     if (typeof Chart === 'undefined') {
//         console.error('Chart.js is not loaded');
//         return;
//     }
//
//     // Đăng ký plugin ChartDataLabels nếu có
//     if (typeof ChartDataLabels !== 'undefined') {
//         Chart.register(ChartDataLabels);
//     }
//
//     // Biểu đồ Order Summary
//     const orderDates = {{ order_dates|safe }};
//     const totalAmounts = {{ total_amounts|safe }};
//     const ctxOrder = document.getElementById('orderChart').getContext('2d');
//     new Chart(ctxOrder, {
//         type: 'line',
//         data: {
//             labels: orderDates,
//             datasets: [{
//                 label: 'Total Amount',
//                 data: totalAmounts,
//                 borderColor: 'blue',
//                 backgroundColor: 'rgba(0, 0, 255, 0.2)',
//                 fill: true,
//             }]
//         },
//         options: {
//             responsive: true,
//             scales: {
//                 x: {
//                     type: 'category',
//                     title: {
//                         display: true,
//                         text: 'Date'
//                     }
//                 },
//                 y: {
//                     title: {
//                         display: true,
//                         text: 'Amount'
//                     }
//                 }
//             }
//         }
//     });
//
//     // Biểu đồ Status Order
//     const successfulOrdersCount = {{ successful_orders_count|default:0 }};
//     const failedOrdersCount = {{ failed_orders_count|default:0 }};
//     const ctxStatus = document.getElementById('statusOrderChart').getContext('2d');
//     new Chart(ctxStatus, {
//         type: 'pie',
//         data: {
//             labels: ['Successful Orders', 'Failed Orders'],
//             datasets: [{
//                 data: [successfulOrdersCount, failedOrdersCount],
//                 backgroundColor: ['#36A2EB', '#FF6384'],
//                 hoverBackgroundColor: ['#48A9F4', '#FF6B91']
//             }]
//         },
//         options: {
//             responsive: true,
//             maintainAspectRatio: false,
//             plugins: {
//                 legend: {
//                     display: true,
//                     position: 'top'
//                 },
//                 datalabels: {
//                     color: '#fff',
//                     font: {
//                         size: 14
//                     },
//                     formatter: (value, context) => {
//                         const total = context.chart.data.datasets[0].data.reduce((acc, val) => acc + val, 0);
//                         const percentage = ((value / total) * 100).toFixed(1);
//                         return `${value} (${percentage}%)`;
//                     }
//                 }
//             }
//         }
//     });
// });