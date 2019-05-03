# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models
from ... import utils


# TODO: add datetime widget
class DateWidget(models.AbstractModel):
    _name = 'cms.form.widget.date'
    _inherit = 'cms.form.widget.mixin'
    _w_template = 'cms_form.field_widget_date'

    # Both default to current lang format.
    w_placeholder = ''
    w_date_format = ''

    def widget_init(self, form, fname, field, **kw):
        widget = super().widget_init(form, fname, field, **kw)
        if 'defaultToday' not in widget.w_data:
            # set today's date by default
            widget.w_data['defaultToday'] = True
        if kw.get('format', widget.w_date_format):
            widget.w_data['dp'] = {
                'format': kw.get('format', widget.w_date_format)
            }
        widget.w_placeholder = kw.get('placeholder', widget.w_placeholder)
        return widget

    def w_extract(self, **req_values):
        value = super().w_extract(**req_values)
        return self.form_to_date(value, **req_values)

    def form_to_date(self, value, **req_values):
        return utils.safe_to_date(value)
