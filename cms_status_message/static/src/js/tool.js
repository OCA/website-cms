odoo.define('cms_status_message.tool', function (require) {
    'use strict';

    var Model = require('web.Model');
    var session = require('web.session');
    var WebsiteModel = new Model('website', session.user_context);
    var core = require('web.core');
    var qweb = core.qweb;
    var ajax = require('web.ajax');

    var load_templates = function load_templates(names) {
        // load existing qweb templates
        var wait_for = [];
        $.each(names, function(){
            var def = $.Deferred();
            if (this in qweb.templates) {
                // already loaded
                def.resolve();
            } else {
                ajax.jsonRpc('/web/dataset/call', 'call', {
                    'model': 'ir.ui.view',
                    'method': 'read_template',
                    'args': [this]
                }).done(function (data) {
                    qweb.add_template(data);
                    def.resolve()
                });
            }
            wait_for.push(def);
        });
        return $.when.apply($, wait_for);
    };

    var MessageTool = {
        add_message: function add_message (msg, options) {
            return WebsiteModel.call('add_status_message', [msg, ], options);
        },
        get_messages: function get_messages() {
            return WebsiteModel.call('get_status_message', []);
        },
        render_messages: function render_messages(msg, selector) {
            var def = $.Deferred();
            load_templates([
                'cms_status_message.message_listing_wrapper',
                'cms_status_message.message_wrapper',
            ]).done(function () {
                // defaults
                var status_message = {
                    'msg': '',
                    'title': null,
                    'type': 'info',
                    'dismissible': true
                };
                // inject user values
                $.extend(status_message, msg);
                // render it
                var result = qweb.render(
                    'cms_status_message.message_listing_wrapper',
                    {status_message: [status_message]}
                );
                if(selector){
                    $(result).prependTo(selector);
                }
                def.resolve(result);
            });
            return def;
        }
    };

    return MessageTool;

});
