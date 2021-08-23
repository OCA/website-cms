# Copyright 2017-2018 Camptocamp - Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "CMS status message",
    "summary": """Basic status messages for your CMS system""",
    "version": "13.0.1.0.1",
    "mainainers": ["simahawk"],
    "license": "LGPL-3",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/website-cms",
    "depends": ["website"],
    "data": [
        "templates/assets.xml",
        "templates/status_message.xml",
        "templates/display_test.xml",
    ],
    "installable": True,
}
