odoo.define("cms_form.ajax", function(require) {
    "use strict";

    var core = require("web.core"),
        animation = require("website.content.snippets.animation");

    animation.registry.CMSFormAjax = animation.Class.extend({
        selector: ".cms_form_wrapper form[data-ajax]",
        events: {
            submit: "submit_form",
        },
        start: function() {
            this.data = this.$el.data("form");
            if (this.$el.data("ajax-onchange")) {
                this.$el.on("change", this.proxy("submit_form"));
            }
            this.$el
                .parents(".cms_form_wrapper")
                .find(this.data.form_content_selector)
                .find(".pagination a[href]")
                .on("click", this.proxy("pager"));
        },
        ajax_submit: function(additional_data) {
            return jQuery.ajax(_.str.sprintf("/cms/ajax/search/%s", this.data.model), {
                data:
                    this.$el.serialize() +
                    "&csrf_token=" +
                    core.csrf_token +
                    (additional_data || ""),
                dataType: "json",
                success: this.proxy("success"),
                error: this.proxy("error"),
            });
        },
        submit_form: function(ev) {
            var $container = this.$container();

            jQuery.blockUI();
            ev.preventDefault();
            $container.empty();

            return this.ajax_submit();
        },
        success: function(data) {
            jQuery.unblockUI();
            var $container = this.$container();

            $container.html(data.content);
            $container.find(".pagination a[href]").on("click", this.proxy("pager"));
        },
        error: function() {
            jQuery.unblockUI();
        },
        pager: function(ev) {
            var $a = jQuery(ev.currentTarget);

            jQuery.blockUI();
            ev.preventDefault();

            return this.ajax_submit("&page=" + $a.data("page"));
        },
        $container: function() {
            return this.$el
                .parents(".cms_form_wrapper")
                .find(this.data.form_content_selector);
        },
    });
});
