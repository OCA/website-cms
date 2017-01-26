odoo.define('cms_form.select2widgets', function (require) {
    'use strict';

    var Model = require('web.Model');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var base = require('web_editor.base');

    var _t = core._t;


    if(!$('.js_select2_m2m_widget').length) {
        return $.Deferred().reject("DOM doesn't contain '.js_select2_m2m_widget'");
    }

    $(document).ready(function () {

        $('input.js_select2_m2m_widget').each(function(){
            var $input = $(this);
            var lastsearch = [];
            $input.select2({
                multiple: true,
                tags: true,
                tokenSeparators: [",", " ", "_"],
                formatResult: function(term) {
                    if (term.isNew) {
                        return '<span class="label label-primary">New</span> ' + _.escape(term.text);
                    } else {
                        return _.escape(term.text);
                    }
                },
                query: function(options) {
                    var domain = [];
                    if (options.term){
                        domain.push([
                          $input.data('search_field') || 'name', 'ilike', '%' + options.term + '%'
                        ])
                    }
                    // TODO: use data.CompundDomain to build domain
                    // ATM it's just in backend assets
                    // and requires both data.js and pyeval.js
                    domain = _.union(domain, $input.data('domain'));
                    ajax.jsonRpc("/web/dataset/call_kw", 'call', {
                        model: $input.data('model'),
                        method: 'search_read',
                        args: [domain],
                        kwargs: {
                            fields: $input.data('fields'),
                            context: base.get_context()
                        }
                    }).then(function(data) {
                        var display_name = $input.data('display_name');
                        data.sort(function(a, b) {
                            return a[display_name].localeCompare(b[display_name]);
                        });
                        var res = {
                            results: []
                        };
                        _.each(data, function(x) {
                            res.results.push({
                                id: x.id,
                                text: x[display_name],
                                isNew: false
                            });
                        });
                        options.callback(res);
                    });
                },
                // Default tags from the input value
                initSelection: function(element, callback) {
                    var data = [];
                    _.each(element.data('init-value'), function(x) {
                        data.push({
                            id: x.id,
                            text: x.name,
                            isNew: false
                        });
                    });
                    element.val('');
                    callback(data);
                },
            });
        });

    });
});
