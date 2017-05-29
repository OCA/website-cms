# -*- coding: utf-8 -*-
# © 2016 Denis Leemann (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import http
from openerp.http import request
from openerp.addons.website_portal.controllers.main import website_account

from openerp.addons.cms_form.controllers.main import FormControllerMixin


class MyAccount(website_account, FormControllerMixin):

    @http.route(['/my/account'], type='http', auth="user", website=True)
    def details(self, **kw):
        """Handle partner form."""
        model = 'res.partner'
        user = request.env['res.users'].browse(request.uid)
        partner = user.partner_id
        return self.make_response(model, model_id=partner.id, **kw)
