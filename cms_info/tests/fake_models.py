# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class FakeModel(models.TransientModel):
    _name = "fake.model"
    _inherit = "website.published.mixin"
    _test_setup_ACL = True

    name = fields.Char()
