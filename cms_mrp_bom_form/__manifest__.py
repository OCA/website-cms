# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'CMS Form MRP Boms',
    'summary': """
        Search forms for MRP Boms in Website""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Eficent, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/website-cms',
    'depends': [
        'website_mrp_bom',
        'cms_form',
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/cms_mrp_bom_form.xml',
    ],
    "demo": [
        'demo/pages.xml'
    ],
    'installable': True,
}
