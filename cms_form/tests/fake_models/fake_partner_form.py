# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models

from odoo.addons.cms_form.models.fields import Serialized  # pylint: disable=W8150


class FakePartnerForm(models.AbstractModel):
    """A test model form."""

    _name = "cms.form.res.partner"
    _inherit = "cms.form"
    _description = "CMS Form test partner form"

    form_model_name = fields.Char(default="res.partner")
    form_model_fields = Serialized(default=("name", "country_id"))
    form_required_fields = Serialized(default=("name", "country_id"))

    custom = fields.Char(default=lambda self: "I am your default")

    def _form_load_custom(self, fname, field, value, **req_values):
        return req_values.get("custom", "oh yeah!")
