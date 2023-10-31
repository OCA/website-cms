# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models

from odoo.addons.cms_form.models.fields import Serialized  # pylint: disable=W8150


class FakeNonPubModel(models.Model):
    _name = "fake.non.publishable"
    _description = "CMS Form fake non publishable model"
    name = fields.Char()


class FakeNonPubModelForm(models.AbstractModel):
    _name = "cms.form.fake.non.publishable"
    _inherit = "cms.form"
    _description = "CMS Form fake non publishable model form"

    form_model_name = fields.Char(default="fake.non.publishable")
    form_model_fields = Serialized(default=("name",))
