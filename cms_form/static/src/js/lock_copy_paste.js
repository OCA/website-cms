import { Interaction } from "@web/public/interaction";
import { registry } from "@web/core/registry";

export class CMSFormLockCopyPaste extends Interaction {
    static selector = ".cms_form_wrapper form .lock_copy_paste";

    dynamicContent = {
        _root: {
            "t-on-cut": (ev) => ev.preventDefault(),
            "t-on-copy": (ev) => ev.preventDefault(),
            "t-on-paste": (ev) => ev.preventDefault(),
            "t-on-contextmenu": (ev) => ev.preventDefault(),
        },
    };
}

registry
    .category("public.interactions")
    .add("cms_form.lock_copy_paste", CMSFormLockCopyPaste);
