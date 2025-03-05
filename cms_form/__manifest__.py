# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "CMS Form",
    "summary": """
        Basic content type form""",
    "version": "14.0.1.0.0",
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
        "templates/assets.xml",
    ],
    "installable": True,
}
