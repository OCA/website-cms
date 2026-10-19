import { Interaction } from "@web/public/interaction";
import { registry } from "@web/core/registry";

export class StatusMessageAutodismiss extends Interaction {
    static selector = ".status_message [data-autodismiss]";

    setup() {
        this.timeout = parseInt(this.el.dataset.autodismissTimeout, 10) || 8000;
    }

    start() {
        this.animation = this.el.animate([{ opacity: 1 }, { opacity: 0 }], {
            duration: this.timeout,
            fill: "forwards",
        });
        this.animation.onfinish = () => this.el.remove();
        this.addListener(this.el, "mouseover", () => this.keepVisible());
        this.registerCleanup(() => this.animation.cancel());
    }

    keepVisible() {
        // Mirror the legacy behaviour: stop fading and show the message again.
        this.animation.cancel();
        this.el.style.opacity = 1;
    }
}

registry
    .category("public.interactions")
    .add("cms_status_message.autodismiss", StatusMessageAutodismiss);
