# Copyright 2018 Simone Orsi - Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

from odoo.addons.cms_form.controllers.main import FormControllerMixin


class MyAccount(CustomerPortal, FormControllerMixin):

    @http.route()
    def account(self, **kw):
        """Replace with cms form."""
        model = 'res.partner'
        partner = request.env.user.partner_id
        return self.make_response(model, model_id=partner.id, **kw)

    def form_model_key(self, model, **kw):
        """Return a valid form model."""
        return 'cms.form.my.account'

    # TODO: just for test/comparison
    @http.route(['/my/account-old'], type='http', auth='user', website=True)
    def account_old(self, **kw):  # pragma: no cover
        """Replace with cms form."""
        return super().account(**kw)
