odoo.define("cms_form.date_widget", function(require) {
    "use strict";

    var sAnimation = require("website.content.snippets.animation");
    var time_utils = require("web.time");

    sAnimation.registry.CMSDateWidget = sAnimation.Class.extend({
        selector: ".cms_form_wrapper form input.js_datepicker",
        start: function() {
            // The datepicker is attached to $fname_display field.
            // The real value is held by the real field input (hidden).
            this.$realField = this.$el.next(
                "#" + this.$el.attr("name").replace("_display", "")
            );
            this.load_options();
            this.setup_datepicker();
        },
        load_options: function() {
            // global options
            this.options = _.omit(this.$el.data("params"), "dp");
            // Datepicker specific ones
            this.picker_options = _.defaults(
                // You can pass datepicker specific options via `dp` attr in params.
                // We don't pass them via `params` otherwise the picker
                // will fail on it if non recognized params are there.
                this.$el.data("params").dp || {},
                {
                    icons: {
                        time: "fa fa-clock-o",
                        date: "fa fa-calendar",
                        up: "fa fa-chevron-up",
                        down: "fa fa-chevron-down",
                    },
                    locale: moment.locale(),
                    format: time_utils.getLangDateFormat(),
                    useCurrent: false,
                }
            );
        },
        setup_datepicker: function() {
            var self = this;
            var placeholder = this.$el.attr("placeholder");
            // Placeholder empty: set default via lang format
            // plahoholder not defined: leave it not set
            if (!placeholder && !_.isUndefined(placeholder)) {
                /* TODO: we should make this translatable. Example:

        lang format in French is `DD.MM.YYYY`
        what the user wants to see is `JJ.MM.AAAA`

        As workaround you can define the placeholder as widget attribute
        and translate it.
        */
                this.$el.attr("placeholder", time_utils.getLangDateFormat());
            }
            // Init bootstrap-datetimepicker
            this.$el.datetimepicker(this.picker_options);
            this.picker = this.$el.data("DateTimePicker");
            this.$el.on("dp.change", function(e) {
                // Update real value field.
                // WARNING: this format should not be touched, it matches server side.
                var real_val = "";
                // E.date is false when no value is set
                if (e.date) {
                    real_val = e.date.format("YYYY-MM-DD");
                }
                self.$realField.val(real_val);
            });
            this._init_date();
            // Enable calendar icon trigger
            this.$el
                .closest(".input-group")
                .find(".js_datepicker_trigger")
                .click(function() {
                    self.picker.show();
                });
        },
        _init_date: function() {
            var self = this;
            // Retrieve current date from real field
            var defaultDate = self.$realField.val();
            if (defaultDate) {
                defaultDate = new Date(defaultDate);
            } else if (self.options.defaultToday) {
                defaultDate = new Date();
            }
            if (defaultDate && !self.$el.val()) {
                this.picker.date(defaultDate);
            }
        },
        destroy: function() {
            this.picker.destroy();
            this._super.apply(this, arguments);
        },
    });
});
