odoo.define('cms_form.date_widget', function (require) {
  'use strict';

  var sAnimation = require('website.content.snippets.animation');
  var time_utils = require('web.time');

  sAnimation.registry.CMSDateWidget = sAnimation.Class.extend({
    selector: ".cms_form_wrapper form input.js_datepicker",
    start: function () {
      // The datepicker is attached to $fname_display field.
      // The real value is held by the real field input (hidden).
      this.$realField = this.$el.next(
        '#' + this.$el.attr('name').replace('_display', '')
      );
      this.load_options();
      this.setup_datepicker();
    },
    load_options: function() {
      // global options
      this.options = _.omit(this.$el.data('params'), 'dp');
      // datepicker specific ones
      this.picker_options = _.defaults(
        // You can pass datepicker specific options via `dp` attr in params.
        // We don't pass them via `params` otherwise the picker
        // will fail on it if non recognized params are there.
        this.$el.data('params').dp || {},
        {
          locale: 'en-us',
          format: time_utils.getLangDateFormat(),
          uiLibrary: 'bootstrap4',
        }
      )
      // Convert gijgo datepicker format to jquery datepicker format for date parsing
        this.picker_options.jquery_format = this.picker_options.format
            .replace(/yy/g, "y")
            .replace(/dddd/g, "DD").replace(/ddd/g, "D")
            .replace(/mmmm/g, "MM").replace(/mmm/g, "M");
    },
    setup_datepicker: function() {
      var self = this;
      var placeholder = this.$el.attr('placeholder');
      // placeholder empty: set default via lang format
      // plahoholder not defined: leave it not set
      if (!placeholder && !_.isUndefined(placeholder)) {
        /* TODO: we should make this translatable. Example:

        lang format in French is `DD.MM.YYYY`
        what the user wants to see is `JJ.MM.AAAA`

        As workaround you can define the placeholder as widget attribute
        and translate it.
        */
        this.$el.attr('placeholder', time_utils.getLangDateFormat());
      }
      // init bootstrap-datetimepicker

      this.picker = this.$el.datepicker(_.defaults(
        this.picker_options, {
            change: function(e) {
                // Update real value field.
                // WARNING: this format should not be touched, it matches server side.
                var real_val = '';
                if (e.target.value) {
                    try {
                        var parsed_date = $.datepicker.parseDate(self.picker_options.jquery_format, e.target.value);
                        real_val = $.datepicker.formatDate('yy-mm-dd', parsed_date);
                        $("#date-error").hide();
                    } catch (err) {
                        // Display error below field, probably a wrong format
                        console.log(err);
                        $("#date-error").show();
                    }
                }
                self.$realField.val(real_val);
            },
            disableDates:  function (date) {
                // Reception of the dates in their isoformat form (string) or as undefined
                const minDateStr = this.params.dp.min_date;
                const maxDateStr = this.params.dp.max_date;
                // Convertion to dates
                const minDate = new Date(minDateStr).setHours(0,0,0,0);
                const maxDate = new Date(maxDateStr).setHours(0,0,0,0);
                // Verify that it is in valid range
                return minDateStr === undefined && maxDateStr === undefined ||
                        minDateStr === undefined && date <= maxDate ||
                        minDate <= date && maxDateStr === undefined ||
                        minDate <= date && date <= maxDate;
            }
        }));
      this._init_date();
    },
    _init_date: function () {
      var self = this;
      // retrieve current date from real field
      var defaultDate = self.$realField.val();
      if (defaultDate && !self.$el.val()) {
        this.picker.value($.datepicker.formatDate(self.picker_options.jquery_format, new Date(defaultDate)));
      }
    },
    destroy: function() {
      this.picker.destroy();
      this._super.apply(this, arguments);
    }
  });

  return sAnimation.registry.CMSDateWidget;

});
