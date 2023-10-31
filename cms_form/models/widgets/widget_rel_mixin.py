# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from odoo import fields, models

from ..fields import Serialized


class RelWidgetMixin(models.AbstractModel):
    _name = "cms.form.widget.rel.mixin"
    _inherit = "cms.form.widget.mixin"
    _description = "CMS Form relation widget mixin"

    w_comodel_name = fields.Char(default="")
    w_domain = Serialized(default=[])
    w_display_field = fields.Char(default="display_name")

    def widget_init(self, form, fname, field, **kw):
        widget = super().widget_init(form, fname, field, **kw)
        widget.w_comodel_name = widget.w_field["relation"]
        for k in ("domain", "display_field"):
            if widget.w_field.get(k):
                setattr(widget, f"w_{k}", widget.w_field.get(k))
        return widget

    @property
    def w_comodel(self):
        return self.env[self.w_comodel_name]
