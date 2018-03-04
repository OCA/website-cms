# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


# `AbstractModel` or `TransientModel` needed to make ACL check happy`
class FakePublishModel(models.TransientModel):
    _name = 'fake.publishable'
    _description = 'Fake publishable'
    _inherit = [
        'website.published.mixin',
    ]
    name = fields.Char()
