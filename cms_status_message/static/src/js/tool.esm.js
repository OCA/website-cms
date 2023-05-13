/** @odoo-module **/

import ajax from "web.ajax";
import {qweb} from "web.core";

export var load_templates = function load_templates(names) {
    // Load existing qweb templates
    var wait_for = [];
    $.each(names, function () {
        var def = $.Deferred();
        if (this in qweb.templates) {
            // Already loaded
            def.resolve();
        } else {
            ajax.jsonRpc("/web/dataset/call", "call", {
                model: "ir.ui.view",
                method: "read_template",
                args: [this],
            }).done(function (data) {
                qweb.add_template(data);
                def.resolve();
            });
        }
        wait_for.push(def);
    });
    return $.when.apply($, wait_for);
};

export class MessageTool {
    add_message(msg, options) {
        return ajax.jsonRpc("/web/dataset/call", "call", {
            model: "ir.http",
            method: "add_status_message",
            args: [[msg], options],
        });
    }
    get_messages() {
        return ajax.jsonRpc("/web/dataset/call", "call", {
            model: "ir.http",
            method: "get_status_message",
            args: [],
        });
    }
    render_messages(msg, selector) {
        var def = $.Deferred();
        load_templates([
            "cms_status_message.message_listing_wrapper",
            "cms_status_message.message_wrapper",
        ]).done(function () {
            // Defaults
            var status_message = {
                msg: "",
                title: null,
                type: "info",
                dismissible: true,
            };
            // Inject user values
            $.extend(status_message, msg);
            // Render it
            var result = qweb.render("cms_status_message.message_listing_wrapper", {
                status_message: [status_message],
            });
            if (selector) {
                $(result).prependTo(selector);
            }
            def.resolve(result);
        });
        return def;
    }
}
