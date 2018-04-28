# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'CMS Toolbar Example',
    'summary': """
        Basic content to showcase the CMS delete content""",
    'version': '11.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'Simone Orsi, Odoo Community Association (OCA)',
    'depends': [
        'website',
        'cms_toolbar',
    ],
    'data': [
        'data/examples.xml',
        'data/ir.model.access.csv',
        'templates/example.xml',
    ],
    'installable': True,
}
