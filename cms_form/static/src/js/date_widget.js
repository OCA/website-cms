odoo.define('cms_form.date_widget', function (require) {
    'use strict';

    $(document).ready(function () {
        $("input.js_datepicker").datetimepicker({
            useSeconds: false,
            icons : {
                time: 'fa fa-clock-o',
                date: 'fa fa-calendar',
                up: 'fa fa-chevron-up',
                down: 'fa fa-chevron-down'
            },
        });
    });

});
