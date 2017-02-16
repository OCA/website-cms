# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'CMS Form',
    'summary': """
        Basic content type form""",
    'version': '9.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Camptocamp SA, Odoo Community Association (OCA)',
    'depends': [
        'website',
        'cms_status_message',
    ],
    'data': [
        'security/cms_form.xml',
        'templates/assets.xml',
        'templates/form.xml',
        'templates/widgets.xml',
    ],
    'demo': [
    ],
}
