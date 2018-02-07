# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'CMS Form',
    'summary': """
        Basic content type form""",
    'version': '11.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'Camptocamp, Odoo Community Association (OCA)',
    'depends': [
        'website',
        'cms_status_message',
    ],
    'data': [
        'security/cms_form.xml',
        # FIXME: remove when fix merged
        'templates/fix_odoo.xml',
        'templates/assets.xml',
        'templates/form.xml',
        'templates/widgets.xml',
    ],
    'installable': True,
}
