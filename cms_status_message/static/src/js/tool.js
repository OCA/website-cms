odoo.define('cms_status_message.tool', function (require) {
    'use strict';

    var core = require('web.core'),
        ajax = require('web.ajax');
    var qweb = core.qweb;

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
          return ajax.jsonRpc('/web/dataset/call', 'call', {
            'model': 'website',
            'method': 'add_status_message',
            'args': [[msg, ], options]
          });
        },
        get_messages: function get_messages() {
            return ajax.jsonRpc('/web/dataset/call', 'call', {
              'model': 'website',
              'method': 'get_status_message',
              'args': []
            });
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
