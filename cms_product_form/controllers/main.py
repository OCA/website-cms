# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import http
from odoo.addons.cms_form.controllers.main import SearchFormControllerMixin


class ProductFormController(http.Controller, SearchFormControllerMixin):
    """Product form controller."""

    @http.route([
        '/products',
        '/products/page/<int:page>',
    ], type='http', auth='public', website=True)
    def list_form(self, **kw):
        """Handle a `form` route.
        """
        model = 'product.template'
        return self.make_response(model, **kw)
