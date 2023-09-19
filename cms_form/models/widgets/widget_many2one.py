# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import json

from odoo import fields, models

from ... import utils
from ..fields import Serialized


class M2OWidget(models.AbstractModel):
    _name = "cms.form.widget.many2one"
    _inherit = "cms.form.widget.rel.mixin"
    _description = "CMS Form M2O widget"

    w_template = fields.Char(default="cms_form.field_widget_m2o")
    w_field_value = fields.Integer()

    @property
    def w_option_items(self):
        return self.w_comodel.search(self.w_domain)

    def w_load(self, **req_values):
        value = super().w_load(**req_values)
        return self.m2o_to_form(value, **req_values)

    def m2o_to_form(self, value, **req_values):
        # important: return False if no value
        # otherwise you will compare an empty recordset with an id
        # in a select input in form widget template.
        if isinstance(value, str) and value.isdigit():
            # number as string
            return int(value) if int(value) > 0 else None
        elif isinstance(value, models.BaseModel):
            return value and value.id or None
        elif isinstance(value, int):
            return value
        return None

    def w_extract(self, **req_values):
        value = super().w_extract(**req_values)
        return self.form_to_m2o(value, **req_values)

    def form_to_m2o(self, value, **req_values):
        val = utils.safe_to_integer(value) or 0
        # we don't want m2o value do be < 1
        return val if val > 0 else None


class M2OMultiWidget(models.AbstractModel):
    _name = "cms.form.widget.many2one.multi"
    _inherit = "cms.form.widget.many2one"
    _description = "CMS Form M2O multi widget"

    w_template = fields.Char(default="cms_form.field_widget_m2o_multi")
    # TODO: not used ATM
    w_display_field = fields.Char(default="display_name")
    w_field_value = Serialized(default=[])

    def m2o_to_form(self, value, **req_values):
        if not value:
            return json.dumps([])
        if isinstance(value, str) and value == req_values.get(self.w_fname):
            value = self.w_comodel.browse(
                # TODO: we should allow customizations of fields to read
                self.w_ids_from_input(value)
            ).read(["name"])
        value = json.dumps(value)
        return value

    def form_to_m2o(self, value, **req_values):
        return self.w_ids_from_input(value) if value else None
