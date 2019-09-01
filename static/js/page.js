$(document).ready(function(){
    $('#registerSection').hide();
    deleteAlertHandler();
    if($('#imgPreview').attr('src') === '#'){
        $('#imgPreview').hide();
    }
});
function deleteAlertHandler() {
$('.icon-alert').click(function(){
   $(this).parent().css('display', 'none');
});
}
// login function switch between login and register
$('#change_section_register, #change_section_login').click(function() {
    $('#registerForm')[0].reset();
    $('#email_status').text('');
    $('#modalLabel').text($(this).attr('data-header'));
    $('#loginSection').toggle();
    $('#registerSection').toggle();

});
 $('#email').keyup(function(){
     if ($('#registerSection').is(':visible')) {
         const emailStatus = $('#email_status');
         $.ajax({
             url: '/email',
             method: 'POST',
             data: $('#registerForm').serialize()
         })
             .done(function (response) {
                 if (!emailStatus.hasClass(response.code)) {
                     emailStatus.removeClass().addClass(response.code)
                 }
                 emailStatus.html(response.message);
                 if (response.code === 'text-danger') {
                     $('#registerSubmit').addClass('disabled')
                 } else {
                     $('#registerSubmit').removeClass('disabled')
                 }
             });
         return false;
     }
 });
 $('#confirm_pw').keyup(function(){
     const password = $('#password').val();
     if (password !== $('#confirm_pw').val()) {
         $('#registerSubmit').addClass('disabled');
         $('#pw_status').addClass('text-danger').html("Passwords don't match")
     } else {
         $('#registerSubmit').removeClass('disabled');
         $('#pw_status').html('')
     }
 });
 const nameRegEx = new RegExp('^[-a-zA-Z]+$');
 $('#registerSubmit').click(function(){
     if ($('#registerSubmit').hasClass('disabled')){
         return false;
     }
     let errors = 0;
     const firstName = $('#firstName').val();
     const lastName = $('#lastName').val();
     const password = $('#password').val();
     if (password.length < 8) {
         errors++;
     }
     if (firstName.length < 2) {
         errors++;
        $('#fn_status').addClass('text-danger').text('First name must be more than 2 characters')
     }
     if (firstName.length >= 2 && !nameRegEx.test(firstName)) {
         errors++;
        $('#fn_status').addClass('text-danger').text('Last name may only contain letters')
     }
     if (lastName.length >= 2 && !nameRegEx.test(lastName)) {
         errors++;
        $('#ln_status').addClass('text-danger').text('Last name may only contain letters')
     }
     if (lastName.length < 2) {
         errors++;
        $('#ln_status').addClass('text-danger').text('Last name must be more than 2 characters')
     }
     if (password !== $('#confirm_pw').val()) {
         errors++;
     }
     deleteAlertHandler();
     if (errors === 0){
         $('#registerForm').submit();
     } else {
         return false;
     }
 });
$('#loginForm').submit(function(){
    // so we can stay on the same route
    const current = window.location.href;
    $.ajax({
        url: '/login',
        method: 'POST',
        data: $(this).serialize()
    })
        .done(function(){
            window.location.href = current;
        });
    return false
});
$('#logoutBtn').click(function(){
    // so we can stay on the same route
    const current = window.location.href;
       $.ajax({
        url: '/logout',
        method: 'POST'
    })
       .done(function(){
           window.location.href = current;
    });
    return false
});
$('#cancelBtn').click(function(){
    window.location.href="/";
});
$('#cancelEditBtn').click(function(){
    window.location.href=`/${$(this).attr('data-page')}/${$(this).attr('datasrc')}`;
});
function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function(e) {
            $('#imgPreview').attr('src', e.target.result);
        };

        reader.readAsDataURL(input.files[0]);
    }
}
$("#fileUpload").change(function() {
    readURL(this);
    $('#imgPreview').show();
});
$('.deleteBlog').click(function() {
    const current = window.location.href;
    const resp = confirm('Are you sure you want to delete blog?');
    if (resp) {
        $.ajax({
            url: `/blogs/${$(this).attr('datasrc')}/delete`,
            method: 'GET'
        })
                .done(function(){
                    window.location.href = current
                })

    }
});
