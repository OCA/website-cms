# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models

from ... import utils


# TODO: add datetime widget
class DateWidget(models.AbstractModel):
    _name = "cms.form.widget.date"
    _inherit = "cms.form.widget.mixin"
    _description = "CMS Form date widget"

    w_template = fields.Char(default="cms_form.field_widget_date")
    # Both default to current lang format.
    w_placeholder = fields.Char(default="")
    w_date_format = fields.Char(default="")
    # change type of field
    w_field_value = fields.Date(default=None)
    w_default_today = fields.Boolean(default=True)

    def widget_init(self, form, fname, field, **kw):
        widget = super().widget_init(form, fname, field, **kw)
        w_data = widget.w_data
        if "defaultToday" not in w_data:
            # set today's date by default
            w_data["defaultToday"] = widget.w_default_today
        if kw.get("format", widget.w_date_format):
            w_data["dp"] = {"format": kw.get("format", widget.w_date_format)}
        widget.w_data = w_data
        widget.w_placeholder = kw.get("placeholder", widget.w_placeholder)
        return widget

    def w_extract(self, **req_values):
        value = super().w_extract(**req_values)
        return self.form_to_date(value, **req_values)

    def form_to_date(self, value, **req_values):
        return utils.safe_to_date(value)
