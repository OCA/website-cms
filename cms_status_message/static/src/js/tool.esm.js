import { rpc } from "@web/core/network/rpc";
import { renderToElement } from "@web/core/utils/render";

export class MessageTool {
    add_message(msg, options) {
        return rpc("/web/dataset/call_kw/ir.http/add_status_message", {
            model: "ir.http",
            method: "add_status_message",
            args: [[msg], options],
            kwargs: {},
        });
    }

    get_messages() {
        return rpc("/web/dataset/call_kw/ir.http/get_status_message", {
            model: "ir.http",
            method: "get_status_message",
            args: [],
            kwargs: {},
        });
    }

    render_messages(msg, selector) {
        // Templates are bundled with the frontend assets (static/src/xml).
        const status_message = {
            msg: "",
            title: null,
            type: "info",
            dismissible: true,
            ...msg,
        };
        const result = renderToElement("cms_status_message.message_listing_wrapper", {
            status_message: [status_message],
        });
        if (selector) {
            document.querySelector(selector)?.prepend(result);
        }
        return result;
    }
}
