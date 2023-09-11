# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class CharWidget(models.AbstractModel):
    _name = "cms.form.widget.char"
    _inherit = "cms.form.widget.mixin"
    _description = "CMS Form char widget"

    w_template = fields.Char(default="cms_form.field_widget_char")
    w_input_type = fields.Char(default="text")


class TextWidget(models.AbstractModel):
    _name = "cms.form.widget.text"
    _inherit = "cms.form.widget.mixin"
    _description = "CMS Form text widget"

    w_template = fields.Char(default="cms_form.field_widget_text")
    w_maxlength = fields.Integer()

    def widget_init(self, form, fname, field, **kw):
        widget = super().widget_init(form, fname, field, **kw)
        widget.w_maxlength = field.get("maxlength") or kw.get("maxlength")
        return widget
