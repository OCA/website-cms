# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


# `AbstractModel` or `AbstractModel` needed to make ACL check happy`
class FakePubModel(models.AbstractModel):
    _name = "fake.publishable"
    _inherit = [
        "cms.info.mixin",
    ]
    _description = "CMS Form fake publishable model form"
    name = fields.Char()

    def _compute_cms_view_url(self):
        for item in self:
            item.url = "/publishable/%d" % item.id


class FakePubModelForm(models.AbstractModel):
    _name = "cms.form.fake.publishable"
    _inherit = "cms.form"
    _description = "CMS Form fake publishable form"
    _form_model = "fake.publishable"
    _form_model_fields = ("name",)
