# Copyright 2018 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http


class Example(http.Controller):

    @http.route(['/cms-toolbar-example'],
                type='http', auth='user', website=True)
    def toolbar_example_list(self, **kw):
        model = http.request.env['cms.toolbar.content.example']
        return http.request.render('cms_toolbar_example.example',
                                   {'main_object': model.search([], limit=1)})
