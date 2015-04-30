$('#filename').change(
    function() {
        if ( !this.files.length ) {
            $('#preview').attr('src', '').css('display','none');
            return;
        }

        var file = $(this).prop('files')[0];
        var fr = new FileReader();
        fr.onload = function() {
            $('#preview').attr('src', fr.result ).css('display','inline');
        }
        fr.readAsDataURL(file);
    }
);
