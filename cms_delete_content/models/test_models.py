# Copyright 2017-2018 Camptocamp - Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, tools

testing = tools.config.get('test_enable')

if testing:
    class PublishResPartner(models.Model):
        _name = "res.partner"
        _inherit = ["res.partner", "website.published.mixin"]

        @api.multi
        def msg_content_deleted(self):
            self.ensure_one()
            return 'Partner deleted.'
