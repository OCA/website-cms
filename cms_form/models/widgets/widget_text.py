# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class CharWidget(models.AbstractModel):
    _name = "cms.form.widget.char"
    _inherit = "cms.form.widget.mixin"
    _description = "CMS Form char widget"
    _w_template = "cms_form.field_widget_char"


class TextWidget(models.AbstractModel):
    _name = "cms.form.widget.text"
    _inherit = "cms.form.widget.mixin"
    _w_template = "cms_form.field_widget_text"
    _description = "CMS Form text widget"
    w_maxlength = None

    def widget_init(self, form, fname, field, **kw):
        widget = super().widget_init(form, fname, field, **kw)
        widget.w_maxlength = field.get("maxlength") or kw.get("maxlength")
        return widget
