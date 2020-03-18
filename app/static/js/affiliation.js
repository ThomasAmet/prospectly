$(document).ready(function(){
    $(document).on('submit', '#id-affiliation-form', function(e){
        e.preventDefault();

        var form = $('#id-affiliation-form')[0];
        var formData = new FormData(form);
        $.ajax({
            type:'POST',
            url: '/affiliation/send-affiliation-email',
            data: formData,
            dataType: 'text',
            processData: false,
            contentType: false,
            success: function(data) { 
                $('#id-affiliation-email-success').removeClass('d-none');
                $('#id-affiliation-email-success').addClass('d-block');
                $('#id-affiliation-error-duplication').removeClass('d-block');
                $('#id-affiliation-error-duplication').addClass('d-none');
                $('#id-affiliation-error-failed').removeClass('d-block');
                $('#id-affiliation-error-failed').addClass('d-none');
            },
            statusCode: {
                510: function() {
                    $('#id-affiliation-email-success').removeClass('d-block');
                    $('#id-affiliation-email-success').addClass('d-none');
                    $('#id-affiliation-error-duplication').removeClass('d-none');
                    $('#id-affiliation-error-duplication').addClass('d-block');
                    $('#id-affiliation-error-failed').removeClass('d-block');
                    $('#id-affiliation-error-failed').addClass('d-none');
                },
                511: function() {
                    $('#id-affiliation-email-success').removeClass('d-block');
                    $('#id-affiliation-email-success').addClass('d-none');
                    $('#id-affiliation-error-duplication').removeClass('d-block');
                    $('#id-affiliation-error-duplication').addClass('d-none');
                    $('#id-affiliation-error-failed').removeClass('d-none');
                    $('#id-affiliation-error-failed').addClass('d-block');
                }
            }
        })
    });
});