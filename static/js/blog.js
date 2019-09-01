$(document).ready(function(){
    deleteAlertHandler();
    if($('#imgPreview').attr('src') === '#'){
        $('#currentImgSection').hide();
        $('#removeImg').hide();
    }
    $('#summernote').summernote({
        height: 400,
        toolbar: [
            [ 'style', [ 'style' ] ],
            [ 'font', [ 'bold', 'italic', 'underline', 'strikethrough', 'superscript', 'subscript', 'clear'] ],
            [ 'fontname', [ 'fontname' ] ],
            [ 'fontsize', [ 'fontsize' ] ],
            [ 'color', [ 'color' ] ],
            [ 'para', [ 'ol', 'ul', 'paragraph', 'height' ] ],
            [ 'insert', [ 'link'] ],
            [ 'view', [ 'undo', 'redo', 'fullscreen', 'help' ] ]
        ]
    })
});
$('#cancelBtn').click(function(){
    window.location.href = `/users/${$(this).attr('datasrc')}`
});
$('#cancelEditBtn').click(function(){
    window.location.href = `/blogs/${$(this).attr('datasrc')}`
});
function deleteAlertHandler() {
    $('.icon-alert').click(function() {
        $(this).parent().css('display', 'none');
    })
}
$('#removeImg').click(function() {
        if (!$('#removeImg').attr('data-target')){
            $('#fileUpload').val('');
            $('#currentImgSection').hide();
            return;
        } else {
            $.ajax({
                url: `/blogs/${$(this).attr('data-target')}/image/delete`,
                method: 'GET'
            })
                .done(function () {
                    $('#removeImg').attr('data-target', null);
                    $('#currentImgSection').hide();
                });
        }
        return false
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
    $('#currentImgSection').show();
    $('#imgPreview').show();
    $('#removeImg').show();
});
