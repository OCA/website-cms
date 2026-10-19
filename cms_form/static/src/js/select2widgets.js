import { Interaction } from "@web/public/interaction";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

import { readData } from "./utils";

/*
Many2many tags input, replacing the select2 widget (select2 is not shipped with Odoo 19 web).
The original input keeps the same contract: its value is a comma-separated list of record ids.
Only existing records can be picked (no tag creation, as the server ignores new tags anyway).
*/
export class CMSFormTagsWidget extends Interaction {
    static selector = "input.js_select2_m2m_widget";

    setup() {
        this.model = readData(this.el, "model");
        this.displayName = readData(this.el, "display_name", "name");
        this.searchField = readData(this.el, "search_field", "name");
        this.fields = readData(this.el, "fields", ["name"]);
        this.domain = readData(this.el, "domain", []);
        this.selected = [...(readData(this.el, "initValue", []) || [])];
    }

    start() {
        this.el.type = "hidden";
        this.buildUI();
        this.renderTags();
        this.addListener(this.textInput, "input", this.debounced(() => this.search(), 250));
        this.addListener(this.list, "click", (ev) => this.onPick(ev));
        this.addListener(this.wrapper, "click", (ev) => this.onRemove(ev));
        this.registerCleanup(() => {
            this.wrapper.remove();
            this.list.remove();
            this.el.type = "text";
        });
    }

    buildUI() {
        this.wrapper = document.createElement("div");
        this.wrapper.className = "form-control d-flex flex-wrap gap-1 align-items-center";
        this.textInput = document.createElement("input");
        this.textInput.type = "text";
        this.textInput.className = "border-0 flex-grow-1 p-0";
        this.textInput.setAttribute("autocomplete", "off");
        this.wrapper.append(this.textInput);
        this.list = document.createElement("ul");
        this.list.className = "list-group";
        this.el.after(this.wrapper, this.list);
    }

    renderTags() {
        this.wrapper.querySelectorAll(".o_tag").forEach((el) => el.remove());
        for (const rec of this.selected) {
            const tag = document.createElement("span");
            tag.className = "o_tag badge text-bg-primary d-inline-flex align-items-center gap-1";
            tag.dataset.id = rec.id;
            tag.textContent = rec.name;
            const remove = document.createElement("button");
            remove.type = "button";
            remove.className = "btn-close btn-close-white o_tag_remove";
            remove.setAttribute("aria-label", "Remove");
            tag.append(remove);
            this.wrapper.insertBefore(tag, this.textInput);
        }
        this.el.value = this.selected.map((rec) => rec.id).join(",");
        this.el.dispatchEvent(new Event("change", { bubbles: true }));
    }

    async search() {
        const term = this.textInput.value.trim();
        this.list.replaceChildren();
        if (!term) {
            return;
        }
        const domain = [[this.searchField, "ilike", term], ...this.domain];
        const records = await rpc(`/web/dataset/call_kw/${this.model}/search_read`, {
            model: this.model,
            method: "search_read",
            args: [domain],
            kwargs: { fields: this.fields, context: {} },
        });
        const known = new Set(this.selected.map((rec) => rec.id));
        records
            .filter((rec) => !known.has(rec.id))
            .sort((a, b) => String(a[this.displayName]).localeCompare(String(b[this.displayName])))
            .forEach((rec) => {
                const item = document.createElement("li");
                item.className = "list-group-item list-group-item-action";
                item.dataset.id = rec.id;
                item.dataset.name = rec[this.displayName];
                item.textContent = rec[this.displayName];
                this.list.append(item);
            });
    }

    onPick(ev) {
        const item = ev.target.closest("li[data-id]");
        if (!item) {
            return;
        }
        this.selected.push({ id: Number(item.dataset.id), name: item.dataset.name });
        this.textInput.value = "";
        this.list.replaceChildren();
        this.renderTags();
        this.textInput.focus();
    }

    onRemove(ev) {
        const button = ev.target.closest(".o_tag_remove");
        if (!button) {
            return;
        }
        const id = Number(button.parentElement.dataset.id);
        this.selected = this.selected.filter((rec) => rec.id !== id);
        this.renderTags();
    }
}

registry.category("public.interactions").add("cms_form.tags", CMSFormTagsWidget);
