# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class FakeModel(models.TransientModel):
    _name = "fake.model"
    _inherit = "cms.info.mixin"
    _description = "Testing fake model"

    name = fields.Char()
