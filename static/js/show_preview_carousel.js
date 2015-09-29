$('.JS_imageArea').change(
    function() {
        var $imageArea = $(this);
        var $file = $imageArea.find('.filename');
        var $preview = $imageArea.find('.preview');

        if ( !$file[0].files.length ) {
            $preview.attr('src', '').css('display','none');
            return;
        }

        var fr = new FileReader();
        fr.onload = function() {
            $preview.attr('src', fr.result ).css({'display':'inline', 'height':250});
        }
        fr.readAsDataURL($file.prop('files')[0]);
    }
);
