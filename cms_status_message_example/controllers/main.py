# Copyright 2017-2018 Camptocamp - Thierry Ducrest
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http


class CMSStatusMsgController(http.Controller):
    """CMS status messge testing route."""

    @http.route([
        '/status-msg/test',
    ], type='http', auth='public', website=True)
    def cms_form(self, **kw):
        """Test the cms status message."""
        msg = http.request.httprequest.args.get('message', 'yes it works')
        msg_title = 'Title'
        for type_ in ('success', 'warning', 'danger', 'info'):
            http.request.website.add_status_message(
                msg, type_=type_, title=msg_title)
        return http.request.render('cms_status_message_example.test_form_page')
