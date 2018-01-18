odoo.define('cms_status_message.tool', function (require) {
    'use strict';

    var session = require('web.session'),
        core = require('web.core'),
        qweb = core.qweb,
        ajax = require('web.ajax');

    // load existing qweb templates
    ajax.jsonRpc('/web/dataset/call', 'call', {
        'model': 'ir.ui.view',
        'method': 'read_template',
        'args': ['cms_status_message.message_listing_wrapper']
    }).done(function (data) {
        qweb.add_template(data);
    });
    ajax.jsonRpc('/web/dataset/call', 'call', {
        'model': 'ir.ui.view',
        'method': 'read_template',
        'args': ['cms_status_message.message_wrapper']
    }).done(function (data) {
        qweb.add_template(data);
    });

    var MessageTool = {
        add_message: function add_message (msg, options) {
          return ajax.jsonRpc('/web/dataset/call', 'call', {
            'model': 'website',
            'method': 'add_status_message',
            'args': [[msg, ], options]
          })
        },
        get_messages: function get_messages() {
            return ajax.jsonRpc('/web/dataset/call', 'call', {
              'model': 'website',
              'method': 'get_status_message',
              'args': []
            })
        },
        render_messages: function render_messages(msg, selector) {
            // defaults
            var status_message = {
                'msg': '',
                'title': null,
                'type': 'info',
                'dismissible': true
            }
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
            return result
        }
    }

    return MessageTool

});
