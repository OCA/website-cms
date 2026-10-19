import { registry } from "@web/core/registry";

function assertHidden(selector, hidden) {
    const el = document.querySelector(selector);
    if (!el || el.hidden !== hidden) {
        throw new Error(`${selector}: expected hidden=${hidden}`);
    }
}

function assertValue(selector, expected) {
    const el = document.querySelector(selector);
    if (!el || el.value !== expected) {
        throw new Error(`${selector}: expected "${expected}", got "${el?.value}"`);
    }
}

registry.category("web_tour.tours").add("cms_form_create_form", {
    steps: () => [
        {
            // master/slave: company name is hidden while kind is "person"
            trigger: "form input[name=name]",
            run: () => assertHidden(".field-company_name", true),
        },
        {
            trigger: "form input[name=name]",
            run: "edit Simone",
        },
        {
            trigger: "select[name=kind]",
            run: "select company",
        },
        {
            trigger: ".field-company_name input[name=company_name]",
            run: "edit Camptocamp",
        },
        {
            // date widget: typed value is mirrored in the server-format field
            trigger: "input[name=birthdate_display]",
            run: "edit 02/01/2000",
        },
        {
            trigger: "input[name=birthdate_display]",
            run: () => assertValue("input[name=birthdate]", "2000-02-01"),
        },
        {
            // many2many tags: search and pick a record
            trigger: ".form-field.field-tag_ids input[type=text]",
            run: "edit Tour",
        },
        {
            trigger: ".form-field.field-tag_ids .list-group-item:contains(Tour tag)",
            run: "click",
        },
        {
            trigger: ".form-field.field-tag_ids .o_tag:contains(Tour tag)",
            run: () => {
                if (!document.querySelector("input[name=tag_ids]").value) {
                    throw new Error("tag_ids: expected a selected id");
                }
            },
        },
    ],
});
