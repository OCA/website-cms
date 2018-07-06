# Copyright 2018 Simone Orsi - Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "CMS toolbar",
    "summary":
        """Toolbar for user actions.""",
    "version": "11.0.1.1.0",
    "category": "Website",
    "website": "https://github.com/OCA/website-cms",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "depends": [
        'cms_info',
        'cms_delete_content',
        'cms_status_message',
    ],
    "data": [
        'templates/assets.xml',
        'templates/toolbar.xml',
    ],
}
