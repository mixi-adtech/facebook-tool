$('input[name="objective"]:radio').change(function() {
    var targetAdSet = ['#adset_install', '#adset_reengagement',];
    $('#adsets').empty();
    $('#account').val('');
    $('#os').val('');
    $('#adset_target').val('');
    $('#deeplink_text').val('');
    $('#deeplink_select').val('');
    $('#deeplink_select optgroup').hide();
    targetAdSet.forEach(function(adset) {
        $(adset).toggle();
    });
});
