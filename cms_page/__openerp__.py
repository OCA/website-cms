# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": "CMS page content",
    "summary": "CMS page content",
    "version": "9.0.1.0.0",
    "category": "Website",
    "website": "https://odoo-community.org/",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    'application': False,
    "depends": [
        'website',
        'cms_form',
        'cms_mixin',
    ],
    "data": [
        # data
        "data/page_types.xml",
        # security
        "security/cms_page_type.xml",
        # views
        # templates
        "templates/page.xml",
    ],
    'external_dependencies': {
        'python': ['requests', ],
    },
}
