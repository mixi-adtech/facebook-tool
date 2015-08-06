$('#form_target').submit(function(){
    $('#form_alert').remove();

    if($('#age_min').val() > $('#age_max').val()){
        var error_msg = $('<div>');
        error_msg.addClass('alert alert-danger');
        error_msg.attr('role', 'alert');
        error_msg.attr('id', 'form_alert');

        error_msg.append('<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span><span class="sr-only">Error:</span>ターゲットの年齢設定が不正です');
        $("#form_main").prepend(error_msg);
        return false;
    }
});

$(".custom_audience_multiple").select2();
$(".excluded_custom_audience_multiple").select2();
$(".country_multiple").select2();
