# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models

from ... import utils
from ..fields import Serialized


class BooleanWidget(models.AbstractModel):
    _name = "cms.form.widget.boolean"
    _inherit = "cms.form.widget.mixin"
    _description = "CMS Form boolean widget"

    w_template = fields.Char(default="cms_form.field_widget_boolean")
    w_wrapper_template = fields.Char(default="cms_form.form_field_label_after_wrapper")
    w_wrapper_css_klass = fields.Char(default="form-check")
    w_true_values = Serialized(default=utils.TRUE_VALUES)
    w_field_value = fields.Boolean()

    def widget_init(self, form, fname, field, **kw):
        widget = super().widget_init(form, fname, field, **kw)
        widget.w_true_values = kw.get("true_values", self.w_true_values)
        widget.w_field_value = widget.w_field_value in self.w_true_values
        return widget

    def w_extract(self, **req_values):
        value = super().w_extract(**req_values)
        return utils.string_to_bool(value, true_values=self.w_true_values)
