# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'CMS Form',
    'summary': """
        Basic content type form""",
    'version': '11.0.1.7.2',
    'license': 'LGPL-3',
    'author': 'Camptocamp, Odoo Community Association (OCA)',
    'depends': [
        'website',
        'cms_info',
        'cms_status_message',
    ],
    'data': [
        'security/cms_form.xml',
        'templates/assets.xml',
        'templates/form.xml',
        'templates/widgets.xml',
    ],
    'installable': True,
}
