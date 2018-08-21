odoo.define('cms_form.date_widget', function (require) {
  'use strict';

  require('web.dom_ready');

  // TODO: migrate to snippet animation
  $(document).ready(function () {
    $("input.js_datepicker").each(function () {
      var $input = $(this);
      var options = _.defaults(
        $input.data('params') || {}, {
          useSeconds: false,
          icons: {
            time: 'fa fa-clock-o',
            date: 'fa fa-calendar',
            up: 'fa fa-chevron-up',
            down: 'fa fa-chevron-down'
          },
          dateFormat: $input.data('format')
        }
      )
      $input.datepicker(options);
      var defaultDate = $input.data('params').defaultDate;
      if (defaultDate) {
        // use custom date
        defaultDate = new Date(defaultDate);
      } else if ($input.data('params').defaultToday) {
        // unless blocked go for today date
        defaultDate = new Date();
      }
      if (defaultDate && !$input.val()) {
        $input.datepicker(
          "setDate", defaultDate
        );
      }
      $input
        .closest('.input-group')
        .find('.js_datepicker_trigger').click(function () {
          $input.datepicker('show');
        });
    });

  });

});
