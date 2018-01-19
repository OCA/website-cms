/* Copyright 2017 OCA/oscar@vauxoo.com
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
odoo.define("cms_form_example.tour", function (require) {
    "use strict";

    var Tour = require("web.Tour");
    var core = require('web.core');
    var _t = core._t;

    Tour.register({
        id: "test_create_partner",
        name: "Try to create a partner",
        path: "/partner/add",
        // mode: "test",
        steps: [
            {
                title: "Fill form with the data to create the 'Demo Partner'",
                element: "button.btn-primary:contains(Submit)",
                onload: function () {
                    $('input[name="name"]').val('Demo Partner');
                    $('input[name="custom"]').val('Demo custom message here!');
                    $('select[name="country_id"] option').each(function(){
                        if (this.text === 'Italy') {
                            $('select[name="country_id"]').val(this.value);
                        }
                    });
                }
            },
            {
                title: _t("Partner created"),
                waitFor: "alert alert-info alert-dismissible:contains(Item created.)",
                content:   _t("This is the new partner. Let's edit it."),
                popover:   { next: _t("Continue") }
            }
        ]
    });

});
