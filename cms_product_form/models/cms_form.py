# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _
from odoo.http import request


class ProductsFormSearch(models.AbstractModel):

    _name = 'cms.form.search.product.template'
    _inherit = 'cms.form.search'
    _form_model = 'product.template'
    _form_model_fields = ('name', )
    _form_required_fields = ('name', )

    default_code = fields.Char()

    @property
    def form_title(self):
        return _('Search Products')

    def form_search_domain(self, search_values):
        domain = super().form_search_domain(search_values)
        if not self._is_website_publisher():
            default_domain = [
                ('website_published', '=', True),
            ]
            domain.extend(default_domain)
        return domain

    @staticmethod
    def _is_website_publisher():
        return request.env['res.users'].has_group(
            'website.group_website_publisher')
