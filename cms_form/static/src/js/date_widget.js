odoo.define('cms_form.date_widget', function (require) {
    'use strict';

    require('web.dom_ready');

    $(document).ready(function () {
        $("input.js_datepicker").each(function(){
            var $input = $(this);
            $input.datepicker({
                useSeconds: false,
                icons : {
                    time: 'fa fa-clock-o',
                    date: 'fa fa-calendar',
                    up: 'fa fa-chevron-up',
                    down: 'fa fa-chevron-down'
                },
                dateFormat : $input.data('format')
            }).datepicker("setDate", new Date());
            $input
                .closest('.input-group')
                .find('.js_datepicker_trigger').click(function(){
                    $input.datepicker('show');
                })
        })


    });

});
