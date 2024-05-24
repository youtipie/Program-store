$(document).ready(function(){
    $("button[data='toggle-modal']").click(function(){
        modal_class = $(this).attr("modal");
        $("div." + modal_class).addClass("is-open");
    });

    $("button.close-but").click(function(){
        $(this).parent().parent().removeClass("is-open");
    });

    $("button[type='submit']").click(function(){
        $(this).parent().parent().removeClass("is-open");
    });

    function displayFormErrors(formId, errors) {
        $("#" + formId + " .form-error").remove();
        $("#" + formId + " .success-message").remove();

        $.each(errors, function(field, error){
            var errorHtml = '<span class="form-error">' + error + '</span>';
            $("#" + formId + " input[name='" + field + "']").after(errorHtml);
        });
    }

     function displaySuccessMessage(formId, message) {
        $("#" + formId + " .form-error").remove();
        $("#" + formId + " .success-message").remove();

        var successHtml = '<div class="success-message">' + message + '</div>';
        $("#" + formId + " .change-but").before(successHtml);
    }

    $("#password-form").submit(function(event){
        event.preventDefault();
        var formData = $(this).serialize();
        $.ajax({
            type: "POST",
            url: $(this).attr("action"),
            data: formData,
            success: function(response){
                displaySuccessMessage("password-form", response.message);
            },
            error: function(xhr, status, error){
                var errors = xhr.responseJSON.errors;
                if (errors) {
                    displayFormErrors("password-form", errors.password_errors);
                }
                console.log(error);
            }
        });
    });

    $("#email-form").submit(function(event){
        event.preventDefault();
        var formData = $(this).serialize();
        $.ajax({
            type: "POST",
            url: $(this).attr("action"),
            data: formData,
            success: function(response){
                displaySuccessMessage("email-form", response.message);
            },
            error: function(xhr, status, error){
                var errors = xhr.responseJSON.errors;
                if (errors) {
                    displayFormErrors("email-form", errors.email_errors);
                }
                console.log(error);
            }
        });
    });

    $("#avatar-form").submit(function(event){
        event.preventDefault();
        var formData = new FormData($(this)[0]);

        $.ajax({
            type: "POST",
            url: $(this).attr("action"),
            data: formData,
            processData: false,
            contentType: false,
            success: function(response){
                displaySuccessMessage("avatar-form", response.message);
                location.reload();
            },
            error: function(xhr, status, error){
                var errors = xhr.responseJSON.errors;
                if (errors) {
                    displayFormErrors("avatar-form", errors.avatar_errors);
                }
                console.log(error);
            }
        });
    });

    $(".avatar-but").click(function(){
        $("#avatar").click();
    });
});