document.addEventListener('DOMContentLoaded', function () {
    const removeButtons = document.querySelectorAll('.remove-favorite-btn');

    removeButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            const vendorId = btn.getAttribute('data-id');

            fetch(`/toggle-favorite/${vendorId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'removed') {
                        btn.closest('.col-md-4').remove(); // Xóa vendor khỏi danh sách
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    });
});