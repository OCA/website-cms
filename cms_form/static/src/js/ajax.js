import {Interaction} from "@web/public/interaction";
import {registry} from "@web/core/registry";

import {readData} from "./utils";

export class CMSFormAjax extends Interaction {
    static selector = ".cms_form_wrapper form[data-ajax]";

    setup() {
        this.data = readData(this.el, "form", {});
        this.container = this.el
            .closest(".cms_form_wrapper")
            ?.querySelector(this.data.form_content_selector);
    }

    start() {
        this.addListener(this.el, "submit", (ev) => this.submitForm(ev));
        if (readData(this.el, "ajaxOnchange")) {
            this.addListener(this.el, "change", (ev) => this.submitForm(ev));
        }
        if (this.container) {
            // Pager links live in the container, which is re-rendered on every
            // response: delegate the click instead of binding each link.
            this.addListener(this.container, "click", (ev) => this.onPagerClick(ev));
        }
    }

    submitForm(ev) {
        ev.preventDefault();
        this.container?.replaceChildren();
        return this.ajaxSubmit();
    }

    onPagerClick(ev) {
        const link = ev.target.closest(".pagination a[href]");
        if (!link) {
            return;
        }
        ev.preventDefault();
        return this.ajaxSubmit({page: readData(link, "page")});
    }

    async ajaxSubmit(extra = {}) {
        const params = new URLSearchParams(new FormData(this.el));
        params.set("csrf_token", odoo.csrf_token);
        for (const [key, value] of Object.entries(extra)) {
            params.set(key, value);
        }
        try {
            const response = await fetch(
                `/cms/ajax/search/${this.data.model}?${params.toString()}`
            );
            const data = await response.json();
            this.render(data.content);
        } catch {
            // Mirror the legacy behaviour: failures are silent, the form stays usable.
        }
    }

    render(content) {
        if (!this.container) {
            return;
        }
        this.container.innerHTML = content;
    }
}

registry.category("public.interactions").add("cms_form.ajax", CMSFormAjax);
