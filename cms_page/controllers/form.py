# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import http
from openerp.addons.cms_form.controllers.main import FormControllerMixin


class FormController(http.Controller, FormControllerMixin):
    """Page form controller."""

    @http.route([
        '/cms/page/create',
        '/cms/page/<model("cms.page"):main_object>/edit',
    ], type='http', auth='user', website=True)
    def cms_form(self, main_object=None, **kw):
        """Handle a `form` route.
        """
        model = 'cms.page'
        return self.make_response(
            model, model_id=main_object and main_object.id, **kw)
