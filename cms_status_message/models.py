# -*- coding: utf-8 -*-
# © 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, api
from openerp.http import request
from openerp import _


class Website(models.Model):
    _inherit = 'website'

    default_status_msg_title = {
        'info': _('Info'),
        'success': _('Success'),
        'danger': _('Error'),
        'warning': _('Warning'),
    }

    @api.model
    def add_status_message(self, msg, mtitle='', mtype='info'):
        """Inject status message in session."""
        mtitle = mtitle or self.default_status_msg_title.get(mtype)
        status_message = {
            'msg': msg,
            'title': mtitle,
            'type': mtype,
        }
        if request.session:
            request.session.setdefault(
                'status_message', []).append(status_message)

    @api.model
    def get_status_message(self):
        if request.session:
            return request.session.pop('status_message', {})
        return {}
