odoo.define('cms_form.date_widget', function (require) {
  'use strict';

  var sAnimation = require('website.content.snippets.animation');

  sAnimation.registry.CMSDateWidget = sAnimation.Class.extend({
    selector: ".cms_form_wrapper form input.js_datepicker",
    start: function () {
      this.load_options();
      this.setup_datepicker();
    },
    load_options: function() {
      this.options = _.defaults(
        this.$el.data('params') || {}, {
          useSeconds: false,
          icons: {
            time: 'fa fa-clock-o',
            date: 'fa fa-calendar',
            up: 'fa fa-chevron-up',
            down: 'fa fa-chevron-down'
          },
          // python = YYYY-MM-DD
          dateFormat: 'yy-mm-dd'
        }
      )
    },
    setup_datepicker: function() {
      var self = this;
      this.$el.datepicker(this.options);
      this.set_default_date();
      this.$el
        .closest('.input-group')
        .find('.js_datepicker_trigger')
        .click(function () {
          self.$el.datepicker('show');
        });
    },
    set_default_date: function () {
      var self = this;
      var defaultDate = self.options.defaultDate;
      if (defaultDate) {
        // use custom date
        defaultDate = new Date(defaultDate);
      } else if (self.options.defaultToday) {
        // unless blocked go for today date
        defaultDate = new Date();
      }
      if (defaultDate && !self.$el.val()) {
        self.$el.datepicker(
          "setDate", defaultDate
        );
      }
    }

  });

});
