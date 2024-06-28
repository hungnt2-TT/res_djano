$(document).ready(function () {
    $('#menuForm').on('submit', function (e) {
        e.preventDefault();
        $.ajax({
            type: 'POST', url: $('#menuForm').attr('action'), data: $(this).serialize(), success: function (response) {
                alert(response.message, response.alert);
                $('#menuForm')[0].reset();
                $('#message').html('');
            }, error: function (response) {
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
    $(".deletelink").on('click', function (e) {
        console.log('delete')
        $('.modal').find('.modal-title').html('Delete Category?');
        $('.modal').find('.modal-body').html('Are you sure you want to delete this category?');
        $('.modal').modal('show');
    });
    $(".btn-submit").on('click', function (e, original) {
        $.ajax({
            url: $(this).data('url'),
            type: 'DELETE', success: function (result) {
                alert(result.message, result.alert);
                location.reload();
            }
        });
    });

});

function alert(message, alertType) {
    $('#message_alert').html('<div class="message_alert alert alert-' + alertType + ' alert-dismissible fade show show-notification" style="position: fixed" role="alert">' + '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' + '<span aria-hidden="true">&times;</span>' + '</button>' + '<strong>' + message + '</strong>' + '</div>')
}