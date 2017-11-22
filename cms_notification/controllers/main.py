# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import http
from openerp.addons.cms_form.controllers.main \
    import FormControllerMixin, SearchFormControllerMixin


class PanelFormController(http.Controller, FormControllerMixin):
    """Notification panel form controller."""

    @http.route([
        '/my/settings/notifications',
    ], type='http', auth='user', website=True)
    def cms_form(self, **kw):
        model = 'res.partner'
        # get current user partner
        model_id = http.request.env.user.partner_id.id
        return self.make_response(
            model, model_id=model_id, **kw)

    def form_model_key(self, model):
        return 'cms.notification.panel.form'


class MyNotificationsController(http.Controller, SearchFormControllerMixin):
    """Personal notifications controller."""

    @http.route([
        '/my/notifications',
    ], type='http', auth='user', website=True)
    def cms_form(self, **kw):
        model = 'res.partner'
        # get current user partner
        model_id = http.request.env.user.partner_id.id
        return self.make_response(
            model, model_id=model_id, **kw)

    def form_model_key(self, model):
        return 'cms.notification.listing'
