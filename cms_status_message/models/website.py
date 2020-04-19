# Copyright 2017-2018 Camptocamp - Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, models
from odoo.http import request


class Website(models.Model):
    _inherit = "website"

    @property
    def default_status_msg_title(self):
        """Some default msg titles."""
        return {
            "info": _("Info"),
            "success": _("Success"),
            "danger": _("Error"),
            "warning": _("Warning"),
        }

    @api.model
    def add_status_message(
        self,
        msg,
        title="",
        type_="info",
        dismissible=True,
        dismiss_options=None,
        session=None,
    ):
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
            "msg": msg,
            "title": title,
            "type": type_,
            "dismissible": bool(dismissible),
        }
        if dismissible and not dismiss_options:
            dismiss_options = self._get_autodismiss_config()
        status_message["dismiss_options"] = dismiss_options or {}
        if session is None:
            session = request.session
        if session is not None:
            session.setdefault("status_message", []).append(status_message)

    def _get_autodismiss_config(self):
        """Retrieve configuration for autodismiss.

        You can create `ir.config_parameter` records to customize:

        * turn on/off -> key="cms_status_message.autodismiss", value="1/0"
        * timeout -> key="cms_status_message.autodismiss_timeout", value="1000"
          (in milliseconds)

        Defaults: ON + 8 seconds timeout.
        """
        params = self.env["ir.config_parameter"].sudo()
        autodismiss = params.get_param("cms_status_message.autodismiss") or ""
        if autodismiss:
            autodismiss = autodismiss.strip() == "1"
        else:
            # default ON
            autodismiss = True
        timeout = params.get_param("cms_status_message.autodismiss_timeout") or ""
        config = {
            "autodismiss": autodismiss,
            "autodismissTimeout": int(timeout.strip()) if timeout.strip() else 8000,
        }
        return config

    @api.model
    def get_status_message(self, session=None):
        """Retrieve status messages from current session.

        :param session: odoo http session.
        By default is taken from the current request.

        :rtype: list.
        """
        session = session or request.session
        if session:
            return session.pop("status_message", [])
        return []
