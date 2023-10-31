# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class CharWidgetMixin(models.AbstractModel):
    _name = "cms.form.widget.char.mixin"
    _inherit = "cms.form.widget.mixin"
    _description = "CMS Form char widget"

    w_template = fields.Char(default="cms_form.field_widget_char")
    w_input_type = fields.Char(default="text")
    w_valid_pattern = fields.Char(help="Used to validate inputs with `pattern` attr")


class CharWidget(models.AbstractModel):
    _name = "cms.form.widget.char"
    _inherit = "cms.form.widget.char.mixin"
    _description = "CMS Form char widget"

    @property
    def html_value(self):
        return self.w_field_value.strip() if self.w_field_value else ""


class TextWidget(models.AbstractModel):
    _name = "cms.form.widget.text"
    _inherit = "cms.form.widget.char.mixin"
    _description = "CMS Form text widget"

    w_template = fields.Char(default="cms_form.field_widget_text")
    w_maxlength = fields.Integer()

    @property
    def html_value(self):
        return self.w_field_value.strip() if self.w_field_value else ""

    def widget_init(self, form, fname, field, **kw):
        widget = super().widget_init(form, fname, field, **kw)
        widget.w_maxlength = field.get("maxlength") or kw.get("maxlength")
        return widget
