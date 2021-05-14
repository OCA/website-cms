# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


# `AbstractModel` or `TransientModel` needed to make ACL check happy`
class FakeNonPubModel(models.TransientModel):
    _name = "fake.non.publishable"
    _description = "CMS Form fake non publishable model"
    name = fields.Char()


class FakeNonPubModelForm(models.AbstractModel):
    _name = "cms.form.fake.non.publishable"
    _inherit = "cms.form"
    _description = "CMS Form fake non publishable model form"
    _form_model = "fake.non.publishable"
    _form_model_fields = ("name",)
