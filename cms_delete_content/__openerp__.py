# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'CMS delete content',
    'summary': """
        Basic features for handling content deletion via frontend.""",
    'version': '9.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Camptocamp,Odoo Community Association (OCA)',
    'depends': [
        'website',
        'cms_status_message',
    ],
    'data': [
        'templates/assets.xml',
        'templates/delete_confirm.xml',
    ],
}
