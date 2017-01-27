# -*- coding: utf-8 -*-
# © 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, api, _
from openerp.http import request


class Website(models.Model):
    _inherit = 'website'

    @property
    def default_status_msg_title(self):
        """Some default msg titles."""
        return {
            'info': _('Info'),
            'success': _('Success'),
            'danger': _('Error'),
            'warning': _('Warning'),
        }

    @api.model
    def add_status_message(self, msg, title='', type_='info',
                           dismissible=True, session=None):
        """Inject status message in session.

        :param msg: the message you want to display.

        :param title: a title for your message.
        By default is taken from `default_status_msg_title` if `type_` matches.
        If you pass `None` the title is removed from the alert box.

        :param type_: the type of message (info, success, etc).
        Is used to provide the proper css klass to the alert box.
        Note: matching a default type is not required at all.
        You can use your custom type to have your alert box styled differently.

        :param dismissible: make the alert dismissible.

        :param session: odoo http session.
        By default is taken from the current request.
        """
        if title is not None:
            title = title or self.default_status_msg_title.get(type_)
        status_message = {
            'msg': msg,
            'title': title,
            'type': type_,
            'dismissible': bool(dismissible),
        }
        session = session or request.session
        if session:
            session.setdefault('status_message', []).append(status_message)

    @api.model
    def get_status_message(self, session=None):
        """Retrieve status messages from current session.

        :param session: odoo http session.
        By default is taken from the current request.

        :rtype: list.
        """
        session = session or request.session
        if session:
            return session.pop('status_message', [])
        return []
