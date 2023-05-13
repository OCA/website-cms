/** @odoo-module **/

import "web.dom_ready";

export class Autodismiss {
    constructor(element) {
        this.$el = $(element);
        this.dimissTimeout = this.$el.data("autodismissTimeout") || 8000;
    }
    handle_autodimiss() {
        const self = this;
        this.$el
            .fadeOut(this.dimissTimeout, function () {
                self.$el.remove();
            })
            .on("mouseover", function () {
                $(this).stop(true).fadeIn(0);
            });
    }
}

$(".status_message [data-autodismiss]").each(function () {
    new Autodismiss(this).handle_autodimiss();
});
