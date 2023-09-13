# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models

from ... import utils


class NumericWidgetMixin(models.AbstractModel):
    _name = "cms.form.widget.numeric.mixin"
    _inherit = "cms.form.widget.char.mixin"
    _description = "CMS Form numeric mixin widget"

    w_template = fields.Char(default="cms_form.field_widget_numeric")
    w_input_type = fields.Char(default="number")
    w_input_min = fields.Char(default="")
    w_input_max = fields.Char(default="")

    def _num_value_to_attr(self, value):
        """Safely convert numeric value for html attr rendering."""
        if value is False or value is None:
            return None
        if isinstance(value, str) and not value.isdigit():
            return None
        return str(value)

    @property
    def html_input_min(self):
        return self._num_value_to_attr(self.w_input_min)

    @property
    def html_input_max(self):
        return self._num_value_to_attr(self.w_input_max)


class IntegerWidget(models.AbstractModel):
    _name = "cms.form.widget.integer"
    _inherit = "cms.form.widget.numeric.mixin"
    _description = "CMS Form integer widget"

    def w_extract(self, **req_values):
        value = super().w_extract(**req_values)
        return utils.safe_to_integer(value)


class FloatWidget(models.AbstractModel):
    _name = "cms.form.widget.float"
    _inherit = "cms.form.widget.char"
    _description = "CMS Form float widget"

    def w_extract(self, **req_values):
        value = super().w_extract(**req_values)
        return utils.safe_to_float(value)
