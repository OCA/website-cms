# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class SelectionWidget(models.AbstractModel):
    _name = 'cms.form.widget.selection'
    _inherit = 'cms.form.widget.mixin'
    _w_template = 'cms_form.field_widget_selection'

    def w_extract(self, **req_values):
        # Handle case where sel options are integers.
        # TODO: unify this using marshallers? See 'hidden' widget
        # Maybe we can have an internal field name
        # and a widget field name. In any case we should be careful
        # and not brake existing forms/widgets.
        value = super().w_extract(**req_values)
        first_value = None
        # use `get` as you might want to use the selection widget
        # for non-Selection fields and just pass options via `w_option_items`.
        if self.w_field.get('selection'):
            # `fields.Selection` does this under the hood
            # to state the PG column type to be used.
            first_value = self.w_field['selection'][0][0]
        # fields.Selection does the same check to determine PG col type
        if first_value and value:
            # convert to same type
            value = type(first_value)(value)
        return value

    @property
    def w_option_items(self):
        return [
            {'value': x[0], 'label': x[1]}
            for x in self.w_field.get('selection', [])
        ]


class RadioSelectionWidget(models.AbstractModel):
    _name = 'cms.form.widget.radio'
    _inherit = 'cms.form.widget.selection'
    _w_template = 'cms_form.field_widget_radio_selection'
    # you can define help message per each options
    # opt value: help msg (can be html too)
    w_options_help = {}

    def widget_init(self, form, fname, field, **kw):
        widget = super(
            RadioSelectionWidget, self).widget_init(form, fname, field, **kw)
        widget.w_options_help = kw.get('options_help') or {}
        return widget
