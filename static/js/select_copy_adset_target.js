$('#adset_target').change(function() {
    $('#adsets').empty();
    $('#account').val('');
    $('#submit').prop('disabled', true);
    if (!$(this).val()) return;
    var account = $(this).val();
    $('#adsets').append('<img src="/static/img/ajaxloader.gif"/>');
    $('#adset_target').prop('disabled', true);
    $.ajax({
        type: 'GET',
        url: '/copy_adset/api/adset/' + account,
        error: function() {
            $('#adsets').empty();
            $('#adsets').append('APIのアクセス制限のため失敗しました。しばらくたってからもう一度選択して下さい。');
            $('#adset_target').prop('disabled', false);
            $('#adset_target').val('');
        },
        success: function(data) {
            if (data && data.result && data.result.length) {
                var table = $('<table>');
                table.addClass('table table-bordered table-hover');
                table.append('<tr><th></th><th>広告セット名</th><<th>キャンペーン名</th>/tr>');
                for (var i=0;i<data.result.length;i++) {
                    var ad = data.result[i];
                    table.append('<tr><td><input type="radio" name="adset_id" value="' + ad.id + '"></td><td>' + ad.name + '</td><td>' + ad.campaign_name + '</td></tr>');
                }
                table.find('tr').click(function(event) {
                    if (event.target.type !== 'radio') {
                        $(':radio', this).trigger('click');
                    }
                });
                $('#adsets').empty();
                $('#adsets').append(table);
            } else {
                $('#adsets').empty();
                $('#adsets').append('対象の広告セットがありません。');
            }
            $('#account').val(account);
            $('#adset_target').prop('disabled', false);
        }
    });
});

$('#adsets').change( function() {
    $('#submit').prop('disabled', !$('input[name=adset_id]:checked').val());
});

