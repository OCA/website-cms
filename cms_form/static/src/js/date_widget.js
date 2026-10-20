import {Interaction} from "@web/public/interaction";
import {registry} from "@web/core/registry";
import {localization} from "@web/core/l10n/localization";
import {parseDate, serializeDate, today} from "@web/core/l10n/dates";

import {readData} from "./utils";

/*
The date picker is attached to the `$fname_display` field.
The real value is held by the hidden field right after it (`fname`), in server format.
*/
export class CMSDateWidget extends Interaction {
    static selector = ".cms_form_wrapper form input.js_datepicker";

    setup() {
        this.options = readData(this.el, "params", {});
        this.realField = this.el.nextElementSibling;
        this.trigger = this.el
            .closest(".input-group")
            ?.querySelector(".js_datepicker_trigger");
    }

    start() {
        const placeholder = this.el.getAttribute("placeholder");
        // Placeholder empty: set default via lang format.
        // Placeholder not defined: leave it not set.
        if (placeholder === "") {
            this.el.setAttribute("placeholder", localization.dateFormat);
        }
        const initial = this.initialValue();
        this.syncRealField(initial);
        this.registerCleanup(
            this.services.datetime_picker
                .create({
                    target: this.el,
                    onApply: (value) => this.syncRealField(value),
                    pickerProps: {type: "date", value: initial},
                })
                .enable()
        );
        if (this.trigger) {
            this.addListener(this.trigger, "click", () => this.el.focus());
        }
    }

    initialValue() {
        // Display value first, then the server value, then today if asked to.
        let value = parseDate(this.el.value) || false;
        if (!value && this.realField?.value) {
            value = parseDate(this.realField.value, {format: "yyyy-MM-dd"}) || false;
        }
        if (!value && this.options.defaultToday) {
            value = today();
        }
        return value;
    }

    syncRealField(value) {
        if (this.realField) {
            // WARNING: this format matches server side, do not touch it.
            this.realField.value = value ? serializeDate(value) : "";
        }
    }
}

registry.category("public.interactions").add("cms_form.date_widget", CMSDateWidget);
