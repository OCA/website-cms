# Copyright 2018 Simone Orsi - Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'CMS Account Form',
    'summary': """CMS replacement for user's account form.""",
    'version': '11.0.1.0.3',
    'license': 'LGPL-3',
    'author': 'Camptocamp,Odoo Community Association (OCA)',
    'depends': [
        'cms_form',
        'portal',
    ],
    'data': [
        'templates/email_warning.xml'
    ],
    "external_dependencies": {
        'python': [
            'validate_email',
        ],
    },
}
