# Copyright 2017-2018 Camptocamp - Thierry Ducrest
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http


class CMSStatusMsgTest(http.Controller):
    """CMS status messge testing routes."""

    display_test_template = "cms_status_message.display_test"

    @http.route(
        "/cms/status-message/display-test",
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def display_test(self, **kw):  # pragma: no cover
        """Test the cms status messages."""
        msg = http.request.httprequest.args.get("message", "yes it works")
        msg_title = "Title"
        for type_ in ("success", "warning", "danger", "info"):
            http.request.website.add_status_message(msg, type_=type_, title=msg_title)
        return http.request.render(self.display_test_template)
