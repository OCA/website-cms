import {Interaction} from "@web/public/interaction";
import {registry} from "@web/core/registry";

import {readData} from "./utils";

/*
Handle master / slave fields automatically.
TODO: explain behavior.
*/

// TODO: support pyeval expressions in JS (see `_form_master_slave_info`).

function inputValue(input) {
    if (input.type === "checkbox") {
        // Value == 'on' => true/false
        return input.checked;
    }
    return input.value;
}

function isPreset(input) {
    return (
        input.tagName === "SELECT" ||
        input.type === "checkbox" ||
        (input.type === "radio" && input.checked) ||
        input.type === "text"
    );
}

export class CMSFormMasterSlave extends Interaction {
    static selector = ".cms_form_wrapper form";

    setup() {
        this.data = readData(this.el, "form", {});
        this.handlers = {
            hide: (slave) => this.setHidden(slave, true),
            show: (slave) => this.setHidden(slave, false),
            readonly: (slave) => this.setReadonly(slave, true),
            no_readonly: (slave) => this.setReadonly(slave, false),
            required: (slave) => this.setRequired(slave, true),
            no_required: (slave) => this.setRequired(slave, false),
        };
    }

    start() {
        for (const [master, actions] of Object.entries(this.data.master_slave || {})) {
            const masterInputs = this.el.querySelectorAll(`[name="${master}"]`);
            for (const [action, mapping] of Object.entries(actions)) {
                const handler = this.handlers[action];
                if (!handler) {
                    continue;
                }
                for (const input of masterInputs) {
                    this.addListener(input, "change", () => {
                        const val = inputValue(input);
                        for (const [slave, values] of Object.entries(mapping)) {
                            if (values.includes(val)) {
                                handler(slave);
                            }
                        }
                    });
                }
            }
            // Apply master/slave rules at load for pre-filled inputs.
            for (const input of masterInputs) {
                if (isPreset(input)) {
                    input.dispatchEvent(new Event("change"));
                }
            }
        }
    }

    slaveInputs(slave) {
        return this.el.querySelectorAll(`[name="${slave}"]`);
    }

    setHidden(slave, hidden) {
        for (const el of this.el.querySelectorAll(`.field-${slave}`)) {
            el.hidden = hidden;
        }
    }

    setReadonly(slave, readonly) {
        for (const input of this.slaveInputs(slave)) {
            if (readonly) {
                input.setAttribute("disabled", "disabled");
            } else {
                input.removeAttribute("disabled");
            }
            input.closest(".form-group")?.classList.toggle("disabled", readonly);
        }
    }

    setRequired(slave, required) {
        for (const input of this.slaveInputs(slave)) {
            if (required) {
                input.setAttribute("required", "required");
            } else {
                input.removeAttribute("required");
            }
            input.closest(".form-group")?.classList.toggle("field-required", required);
        }
    }
}

registry
    .category("public.interactions")
    .add("cms_form.master_slave", CMSFormMasterSlave);
