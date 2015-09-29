$('#template').change(function() {
    var messages = [
        "template message"
    ];
    $('#creative_name').val($('[name=template] option:selected').text());
    $('#message').val(messages[this.selectedIndex]);
});
