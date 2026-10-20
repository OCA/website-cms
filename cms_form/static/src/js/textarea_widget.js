import {Interaction} from "@web/public/interaction";
import {registry} from "@web/core/registry";

import {readData} from "./utils";

/*
Show how many characters are left on textareas with a `maxlength`.
The counter is the next `.text-counter` sibling, or the element matching `data-counter`.
*/
export class CMSFormTextareaCounter extends Interaction {
    static selector = "textarea[maxlength]";

    setup() {
        this.maxlength = parseInt(this.el.getAttribute("maxlength"), 10);
    }

    start() {
        this.addListener(this.el, "input propertychange", () => this.updateCounter());
        this.updateCounter();
    }

    get counter() {
        const selector = readData(this.el, "counter");
        if (selector) {
            return document.querySelector(selector);
        }
        return this.el.parentElement?.querySelector(".text-counter");
    }

    updateCounter() {
        const counter = this.counter;
        if (!counter) {
            return;
        }
        const left = Math.max(this.maxlength - this.el.value.length, 0);
        counter.value = left;
    }
}

registry
    .category("public.interactions")
    .add("cms_form.textarea_counter", CMSFormTextareaCounter);
