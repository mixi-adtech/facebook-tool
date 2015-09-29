$('#campaign_id').change(function() {
    var text = $("#campaign_id option:selected").text();
    var os = text.match(/android/) ? "android" : "ios";
    $('#os').val(os);
});
