# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MrpBomFormSearch(models.AbstractModel):

    _name = 'cms.form.search.mrp.bom'
    _inherit = 'cms.form.search'
    _form_model = 'mrp.bom'
    _form_model_fields = ('name', 'code', )

    def form_search_domain(self, search_values):
        domain = super().form_search_domain(search_values)
        default_domain = [
            ('product_tmpl_id.website_published', '=', True),
            ('website_published', '=', True),
        ]
        domain.extend(default_domain)
        return domain
