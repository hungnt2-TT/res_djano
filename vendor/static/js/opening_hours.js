$(document).ready(function () {
    $('.add_hour').click(function (e) {
        e.preventDefault();
        console.log('Add hour');
        var day = document.getElementById('id_day').value;
        var from_hour = document.getElementById('id_from_hour').value;
        var to_hour = document.getElementById('id_to_hour').value;
        var is_closed = document.getElementById('id_is_closed').checked;
        var csrf = $('input[name=csrfmiddlewaretoken]').val();
        var url = document.getElementById('opening_hours_add').value;
        console.log('day', url);
        if (is_closed) {
            is_closed = 'True';
            condition = 'day != ""';
        } else {
            is_closed = 'False';
            condition = 'day != "" && from_hour != "" && to_hour != ""';
        }

        if (eval(condition)) {
            $.ajax({
                type: 'POST', url: url, data: {
                    'day': day,
                    'from_hour': from_hour,
                    'to_hour': to_hour,
                    'is_closed': is_closed,
                    'csrfmiddlewaretoken': csrf
                }, success: function (response) {
                    if (response.status === 'success') {
                        let isClosedText = response.is_closed ? 'Closed' : `${response.from_hour} - ${response.to_hour}`;

                        let html = `
                                <tr ${response.is_closed === 'Closed' ? 'class="closed-hour"' : ''}>
                                <td style="text-align: center"><b>${response.day}</b></td>
                                <td style="text-align: center">${isClosedText}</td>
                                <td style="text-align: center">
                                    <a href="#" class="edit_hour" data-id="${response.id}" data-url="/vendor/opening_hours_edit/${response.id}">Edit</a> | 
                                    <a href="#" class="delete_hour" data-id="${response.id}" data-url="/vendor/opening_hours_delete/${response.id}">Remove</a>
                                </td>
                            </tr>`;

                        $('.opening_hours_vendor').append(html);

                    }
                    console.log('success', response);
                }, error: function (response) {
                    Swal.fire({
                        icon: 'error', title: 'Oops...', text: 'Something went wrong!',
                    });
                }
            });

        } else {
            Swal.fire({
                icon: 'error', title: 'Oops...', text: 'Please fill all fields!',
            })
        }
        ;
    })
    $(document).on('click', '.delete_hour', function (e) {
        console.log('Delete hour');
        e.preventDefault();

        var csrf = $('input[name=csrfmiddlewaretoken]').val();
        var url = $(this).data('url');

        Swal.fire({
            title: 'Are you sure?',
            text: "You won't be able to revert this!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, delete it!'
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: url,
                    type: 'DELETE',
                    data: {csrfmiddlewaretoken: csrf},
                    success: function (response) {
                        if (response.status === 'success') {
                            Swal.fire('Deleted!', 'The opening hour has been deleted.', 'success');
                            $(e.target).closest('tr').remove();
                        } else {
                            Swal.fire('Error!', response.message, 'error');
                        }
                    },
                    error: function () {
                        Swal.fire('Error!', 'Something went wrong.', 'error');
                    }
                });
            }
        });
    });
    $(document).on('click', '.edit_hour', function (e) {
        e.preventDefault();

        let editUrl = $(this).data('url');
        let csrf = $('input[name=csrfmiddlewaretoken]').val();
        let row = $(this).closest('tr');

        let timeText = row.find('td:nth-child(2)').text().trim();
        let isClosed = timeText === 'Closed';
        let fromHour = '', toHour = '';

        if (!isClosed) {
            let timeRange = timeText.replace(/\s+/g, ' ').trim();
            let timeParts = timeRange.split(' - ');
            fromHour = timeParts[0];
            toHour = timeParts[1];
        }

        Swal.fire({
            title: 'Edit Opening Hour',
            html: `
            <input id="day" class="swal2-input" placeholder="Day" value="${row.find('td:first').text().trim()}">
            <input id="from_hour" class="swal2-input" placeholder="From Hour" value="${fromHour}">
            <input id="to_hour" class="swal2-input" placeholder="To Hour" value="${toHour}">
            <label style="display: flex; align-items: center; justify-content: center; gap: 5px; margin-top: 10px;">
                <input id="is_closed" type="checkbox" ${isClosed ? 'checked' : ''}> Closed
            </label>
            <hr>
        `,
            focusConfirm: false,
            preConfirm: () => {
                // Lấy dữ liệu từ các input trong modal
                return {
                    day: document.getElementById('day').value.trim(),
                    from_hour: document.getElementById('from_hour').value.trim(),
                    to_hour: document.getElementById('to_hour').value.trim(),
                    is_closed: document.getElementById('is_closed').checked,
                };
            }
        }).then((result) => {
            if (result.isConfirmed) {
                let data = result.value;

                // Gửi yêu cầu AJAX để chỉnh sửa
                $.ajax({
                    url: editUrl,
                    type: 'POST',
                    headers: {'X-Requested-With': 'XMLHttpRequest'},
                    data: {
                        csrfmiddlewaretoken: csrf,
                        day: data.day,
                        from_hour: data.from_hour,
                        to_hour: data.to_hour,
                        is_closed: data.is_closed,
                    },
                    success: function (response) {
                        if (response.status === 'success') {
                            let isClosedText = response.is_closed === 'Closed' ? 'Closed' : `${response.from_hour} - ${response.to_hour}`;
                            console.log('isClosedText', isClosedText);
                            row.html(`
            <td style="text-align: center"><b>${response.day}</b></td>
            <td style="text-align: center">${isClosedText}</td>
            <td style="text-align: center">
                <a href="#" class="edit_hour" data-id="${response.id}" data-url="/vendor/opening_hours_edit/${response.id}">Edit</a> | 
                <a href="#" class="delete_hour" data-id="${response.id}" data-url="/vendor/opening_hours_delete/${response.id}">Remove</a>
            </td>
        `);


                            Swal.fire('Success!', response.message, 'success');
                        } else {
                            Swal.fire('Error!', response.message, 'error');
                        }
                    },
                    error: function () {
                        Swal.fire('Error!', 'Unable to update opening hour!', 'error');
                    }
                });
            }
        });
    });
})