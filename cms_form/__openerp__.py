# -*- coding: utf-8 -*-
# Copyright 2016 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'CMS Form',
    'summary': """
        Basic content type form""",
    'version': '9.1.0a1',
    'license': 'AGPL-3',
    'author': 'Simone Orsi,Odoo Community Association (OCA)',
    'depends': [
        'website',
        'cms_status_message',
    ],
    'data': [
        'security/cms_form.xml',
        'templates/assets.xml',
        'templates/form.xml',
    ],
    'demo': [
    ],
}
