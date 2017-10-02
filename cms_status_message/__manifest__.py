# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'CMS status message',
    'summary': """Basic status messages for your CMS system""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Camptocamp,Odoo Community Association (OCA)',
    'depends': [
        'website',
    ],
    'data': [
        'templates/assets.xml',
        'templates/status_message.xml',
    ],
    'installable': True,
}
