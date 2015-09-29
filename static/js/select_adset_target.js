$('#adset_target').change(function() {
    $('#adsets').empty();
    $('#account').val('');
    $('#os').val('');
    $('#deeplink_text').val('');
    $('#deeplink_select').val('');
    $('#deeplink_select optgroup').hide();
    $('#submit').prop('disabled', true);
    $('.campaign_label').each(function() {
        $(this).attr('disabled', 'disabled');
    });
    if (!$(this).val()) return;
    var targets = $(this).val().split('_');
    var account = targets[0];
    var os = targets[1];
    var objective = targets[2] + '_' + targets[3] + '_' + targets[4];
    $('#adsets').append('<img src="/static/img/ajaxloader.gif"/>');
    $('#adset_target').prop('disabled', true);
    $('#title').focus();
    $.ajax({
        type: 'GET',
        url: '/add_creative/api/adset/' + account + '/' + os + '/' + objective,
        error: function() {
            $('#adsets').empty();
            $('#adsets').append('APIのアクセス制限のため失敗しました。しばらくたってからもう一度選択して下さい。');
            $('#adset_target').prop('disabled', false);
            $('#adset_target').val('');
            $('.campaign_label').each(function() {
                $(this).removeAttr('disabled');
            });
        },
        success: function(data) {
            if (data && data.result && data.result.length) {
                var table = $('<table>');
                table.addClass('table table-bordered table-hover');
                table.append('<tr><th><input type="checkbox" checked id="check_all" checked></th><th>キャンペーン名</th><th>広告セット名</th><th>クリエイティブ数</th></tr>');
                for (var i=0;i<data.result.length;i++) {
                    var ad = data.result[i];
                    table.append('<tr><td><input checked type="checkbox" name="adset_ids" value="' + ad.id + '" id="chk_' + ad.id + '"></td><td>' + ad.campaign_name + '</td><td>' + ad.name + '</td><td>' + ad.creative_count + '</td></tr>');
                    if (parseInt(ad.creative_count, 10) < 50 && ad.campaign_objective == $('input[name="objective"]:radio:checked').val()) {
                        table.find('#chk_' + ad.id).on('change', function() {
                            var checked = $('input[name="adset_ids"]:checked').map(function() {
                                return $(this).val();
                            }).get();
                            $('#submit').prop('disabled', checked.length == 0);
                        });
                    } else {
                        table.find('#chk_' + ad.id).remove();
                    }
                }
                table.find('tr').click(function(event) {
                    if (event.target.type !== 'checkbox') {
                        $(':checkbox', this).trigger('click');
                    }
                });
                $('#adsets').empty();
                $('#adsets').append(table);
                $('#check_all').on('change', function() {
                    $('input[name=adset_ids]').prop('checked', this.checked);
                    $('#submit').prop('disabled', !this.checked);
                });
            } else {
                $('#adsets').empty();
                $('#adsets').append('対象の広告セットがありません。');
            }
            $('#account').val(account);
            $('#os').val(os);
            $('#deeplink_select optgroup#deeplink_' + account + '_' + os).show();
            $('#adset_target').prop('disabled', false);
            $('.campaign_label').each(function() {
                $(this).removeAttr('disabled');
            });
            $('#submit').prop('disabled', !$('input[name=adset_ids]').prop('checked'));
        }
    });
});
