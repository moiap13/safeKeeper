$form.on('submit', function(e) {
    if ($form.hasClass('is-uploading')) return false;

    $form.addClass('is-uploading').removeClass('is-error');

    if (isAdvancedUpload) {
        // ajax for modern browsers
        e.preventDefault();

        var ajaxData = new FormData($form.get(0));

        //var object = {};
        if (droppedFiles) {
            ajaxData = new FormData();
            $.each( droppedFiles, function(i, file) {
                //object[$input.attr('name')+i] = file;
                ajaxData.append($input.attr('name'), file);
            });
        }

        //var json = JSON.stringify(object);

        $.ajax({
            url: $form.attr('action'),
            type: $form.attr('method'),
            data: ajaxData,
            dataType: 'json',
            cache: false,
            contentType: false,
            processData: false,
            complete: function() {
              $form.removeClass('is-uploading');
            },
            success: function(data) {
                alert(data);
                $form.addClass( data.success == true ? 'is-success' : 'is-error' );
                if (!data.success) $errorMsg.text(data.error);
            },
            error: function() {
              // Log the error, show an alert, whatever works for you
            }
        });
    } else {
        // ajax for legacy browsers
        var iframeName  = 'uploadiframe' + new Date().getTime();
        $iframe   = $('<iframe name="' + iframeName + '" style="display: none;"></iframe>');

        $('body').append($iframe);
        $form.attr('target', iframeName);

        $iframe.one('load', function() {
        var data = JSON.parse($iframe.contents().find('body' ).text());
        $form
          .removeClass('is-uploading')
          .addClass(data.success == true ? 'is-success' : 'is-error')
          .removeAttr('target');
        if (!data.success) $errorMsg.text(data.error);
            $form.removeAttr('target');
            $iframe.remove();
        });
    }
});