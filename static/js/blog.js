$(document).ready(function(){
});
$('#cancelBtn').click(function(){
    window.location.href = '/'
});
$('#cancelBtnEdit').click(function(){
    window.location.href = `/blogs/${$(this).attr('datasrc')}`
});
$('#logoutBtn').click(function(){
    const redirection = $(this).attr('data-redirect');
       $.ajax({
        url: '/logout',
        method: 'POST',
           data: {'url': redirection}
    })
       .done(function(){
           window.location.href = redirection;
    })
});
