# Copyright 2017 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.addons.cms_form.controllers.main import SearchFormControllerMixin
from odoo.addons.cms_form.controllers.main import FormControllerMixin


class PartnerFormController(http.Controller, FormControllerMixin):
    """Partner form controller."""

    @http.route([
        '/partner/add',
        '/partner/<model("res.partner"):main_object>/edit',
    ], type='http', auth='user', website=True)
    def cms_form(self, main_object=None, **kw):
        """Handle a `form` route.
        """
        model = 'res.partner'
        return self.make_response(
            model, model_id=main_object and main_object.id, **kw)


class PartnerListing(http.Controller, SearchFormControllerMixin):
    """Partner search form controller."""

    @http.route([
        '/partners',
        '/partners/page/<int:page>',
    ], type='http', auth="public", website=True)
    def market(self, **kw):
        model = 'res.partner'
        return self.make_response(model, **kw)
