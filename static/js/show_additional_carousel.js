$(function() {
    var slot = ['4', '5'];

    $.each(slot, function(i, value) {
        $('.JS_checkbox' + value).change(
            function() {
                var slot_count = $(this).val();
                if($(this).prop('checked')) {
                    $('.JS_slot' + slot_count).show().find('input').removeAttr('disabled');
                } else {
                    $('.JS_slot' + slot_count).hide().find('input').attr('disabled', 'disabled');
                }
            }
        );
    });
});
