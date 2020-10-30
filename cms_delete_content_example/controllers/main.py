# Copyright 2017-2018 Rémy Taymans
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http


class ExampleModelDeleteControler(http.Controller):
    @http.route(
        ["/list-delete-content-example"], type="http", auth="user", website=True,
    )
    def list_delete_content_example(self, **kw):
        model = http.request.env["cms.delete.content.example"]
        return http.request.render(
            "cms_delete_content_example.list_examples", {"examples": model.search([])},
        )
