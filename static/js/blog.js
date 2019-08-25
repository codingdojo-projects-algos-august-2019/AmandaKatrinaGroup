$(document).ready(function(){
});
$('#cancelBtn').click(function(){
    window.location.href = '/'
});
$('#cancelBtnEdit').click(function(){
    window.location.href = `/blogs/${$(this).attr('datasrc')}`
});
