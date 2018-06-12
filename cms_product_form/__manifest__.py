# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'CMS Form Products',
    'summary': """
        Search forms for products""",
    'version': '11.0.1.0.0',
    'category': 'Website CMS',
    'website': "https://github.com/OCA/website-cms",
    'license': 'AGPL-3',
    'author': 'Eficent, '
              'Odoo Community Association (OCA)',
    'depends': [
        'website_product',
        'cms_form',
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/cms_product_form.xml',
    ],
    "demo": [
        'demo/pages.xml'
    ],
    'installable': True,
}
