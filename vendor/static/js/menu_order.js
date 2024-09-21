$(document).ready(function () {


    // initListPagination();

    $('#menuForm').on('submit', function (e) {
        e.preventDefault();
        let submitButtonValue = $(document.activeElement).val();

        console.log('submitButtonValue', submitButtonValue);
        let formData = $(this).serializeArray();
        if (submitButtonValue === 'Add Food Item') {
            formData.push({name: 'submit', value: 'add_food'});
        }
        if (submitButtonValue === 'Add Category') {
            formData.push({name: 'submit', value: 'add_category'});
        }
        let filteredData = formData.filter(function (item) {
            if (submitButtonValue === 'Add Food Item') {
                return true;
            }
            if (submitButtonValue === 'Add Category') {
                return true;
            }
            return false;
        });
        console.log('filteredData', filteredData);
        $.ajax({
            type: 'POST',
            url: $('#menuForm').attr('action'),
            data: $.param(filteredData),
            success: function (response) {
                alert(response.message, response.alert);
                $('#menuForm')[0].reset();
                $('#message').html('');
                window.location.reload();
            },
            error: function (response) {
                let errors = response.responseJSON.errors;
                let errorMessages = '<ul>';
                for (let field in errors) {
                    errors[field].forEach(function (error) {
                        errorMessages += error + '<br>';
                    });
                }
                $('#message').html('<div class="text-danger">' + errorMessages + '</div>');
                alert(response.responseJSON.message, response.responseJSON.alert);
            }
        });
    });
    $(".delete-link").on('click', function (e) {
        e.preventDefault();
        let transactionId = $(this).data('id');
        $('.modal').find('.modal-title').html('Delete Category?');
        $('.modal').find('.modal-body').html('Are you sure you want to delete this category?');
        $('.btn-submit').data('id', transactionId);
        $('#delete-confirmation').show();
    });
    $(".btn-submit").on('click', function (e, original) {
        e.preventDefault();
        let category_id = $(this).data('id');
        $.ajax({
            url: 'menu_delete_detail/' + category_id, type: 'DELETE', success: function (result) {
                alert(result.message, result.alert);
                location.reload();
            }, error: function (response) {
                alert(response.message, response.alert);
            }
        });
    });

    $(".edit-link").on('click', function (e) {
        e.preventDefault();
        let transactionId = $(this).data('id');
        console.log(transactionId);

        $('.btn-update').data('id', transactionId);
    });
    $(".btn-update").on('click', function (e) {
        e.preventDefault();
        let transactionId = $(this).data('id');
        console.log('transactionId = ', transactionId);
        let data = {
            'category_name': $('#category_name' + transactionId).val(),
            'category_description': $('#category_description' + transactionId).val(),
        }
        console.log('data', data);
        $.ajax({
            url: 'menu_edit_detail/' + transactionId,
            type: 'PATCH',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function (result) {
                alert(result.message, result.alert);
                location.reload();
            },
            error: function (response) {
                alert(response.message, response.alert);
            }
        });
    });

    function initListPagination() {
        var options = {
            valueNames: [
                'sort01', 'sort02', 'sort03', 'sort04', 'sort05',
                {data: ['sort06']}, 'sort07', 'sort08',
                {data: ['sort09']}
            ],
            page: 100,
            pagination: {
                innerWindow: 11,
                left: 0,
                right: 0,
                paginationClass: "pagination",
            }
        };

        listObj = new List('menu-list', options);
        listObj.on('updated', function (list) {
            let totalRecord = list.items.length;
            let startItemIndex = list.i;
            let endItemIndex = startItemIndex + list.visibleItems.length - 1;
            $('.summary-pagination').html(`${totalRecord}件中　${startItemIndex}件 〜 ${endItemIndex}件`);

        });
    }

    // $('.nav-item ').first().addClass('active');
    // $('.nav-item .menu-sidebar  ').click(function (e) {
    //     e.preventDefault();
    //     $('.nav-item').removeClass('active');
    //     $(this).parent('.nav-item').addClass('active');
    // });
});

function alert(message, alertType) {
    $('#message_alert').html('<div class="message_alert alert alert-' + alertType + ' alert-dismissible fade show show-notification" style="position: fixed" role="alert">' + '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' + '<span aria-hidden="true">&times;</span>' + '</button>' + '<strong>' + message + '</strong>' + '</div>')
}