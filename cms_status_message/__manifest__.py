# Copyright 2017 Camptocamp - Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "CMS status message",
    "summary": """Basic status messages for your CMS system""",
    "version": "16.0.1.0.0",
    "maintainers": ["simahawk"],
    "license": "LGPL-3",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/website-cms",
    "depends": ["web", "portal"],
    "data": [
        "templates/status_message.xml",
        "templates/display_test.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "cms_status_message/static/src/js/tool.esm.js",
            "cms_status_message/static/src/js/autodismiss.esm.js",
        ],
    },
    "installable": True,
}
