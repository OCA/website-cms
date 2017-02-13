# -*- coding: utf-8 -*-

from openerp import http
from openerp.addons.cms_form.controllers.main import FormControllerMixin


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
