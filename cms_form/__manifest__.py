# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "CMS Form",
    "summary": """
        Basic content type form""",
    "version": "16.0.1.1.0",
    "license": "LGPL-3",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["simahawk"],
    "website": "https://github.com/OCA/website-cms",
    "depends": [
        "cms_info",
        "cms_status_message",
        # TODO: get rid of portal too
        "portal",
        "base_sparse_field",
    ],
    "data": [
        "security/cms_form.xml",
        "templates/form.xml",
        "templates/widgets.xml",
        "templates/portal.xml",
    ],
    "installable": True,
    "assets": {
        "web.assets_frontend": [
            "cms_form/static/src/scss/cms_form.scss",
            "cms_form/static/src/scss/progressbar.scss",
            # TODO: review them all w/ modern JS
            "cms_form/static/src/js/select2widgets.js",
            "cms_form/static/src/js/date_widget.js",
            "cms_form/static/src/js/textarea_widget.js",
            "cms_form/static/src/js/master_slave.js",
            "cms_form/static/src/js/lock_copy_paste.js",
            "cms_form/static/src/js/ajax.js",
        ],
    },
}
