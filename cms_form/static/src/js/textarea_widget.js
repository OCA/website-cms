odoo.define('cms_form.textarea_widget', function (require) {
    'use strict';

    var ajax = require('web.ajax');

    $(document).ready(function () {
        $('textarea[maxlength]').bind('input propertychange', function(){
            var $self = $(this),
                maxlength = parseInt($self.attr('maxlength')),
                length = $self.val().length,
                left = maxlength - length,
                $counter = $self.siblings('.text-counter');
            if ($self.data('counter')) {
                $counter = $($self.data('counter'));
            }
            if (left < 0) {
                left = 0;
            }
            $counter.val(left);
        }).trigger('input');
    });

});
