# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import json
from odoo import models


class Widget(models.AbstractModel):
    _name = 'cms.form.widget.mixin'

    # use `w_` prefix as a namespace for all widget properties
    _w_template = ''
    _w_css_klass = ''

    def widget_init(self, form, fname, field,
                    data=None, subfields=None,
                    template='', css_klass='', **kw):
        widget = self.new()
        widget.w_form = form
        widget.w_form_model = form.form_model
        widget.w_record = form.main_object
        widget.w_form_values = form.form_render_values
        widget.w_fname = fname
        widget.w_field = field
        widget.w_field_value = widget.w_form_values.get(
            'form_data', {}).get(fname)
        widget.w_data = data or {}
        widget.w_subfields = subfields or field.get('subfields', {})
        widget._w_template = template or self._w_template
        widget._w_css_klass = css_klass or self._w_css_klass
        return widget

    def render(self):
        return self.env.ref(self.w_template).render({'widget': self})

    @property
    def w_template(self):
        return self._w_template

    @property
    def w_css_klass(self):
        return self._w_css_klass

    def w_load(self, **req_values):
        """Load value for current field in current request."""
        value = self.w_field.get('_default')
        # we could have form-only fields
        if self.w_record and self.w_fname in self.w_record:
            value = self.w_record[self.w_fname] or value
        # maybe a POST request with new values: override item value
        value = req_values.get(self.w_fname, value)
        return value

    def w_extract(self, **req_values):
        """Extract value from form submit."""
        return req_values.get(self.w_fname)

    def w_check_empty_value(self, value, **req_values):
        # `None` values are meant to be ignored as not changed
        return value in (False, '')

    @staticmethod
    def w_ids_from_input(value):
        """Convert list of ids from form input."""
        return [int(rec_id.strip())
                for rec_id in value.split(',') if rec_id.strip().isdigit()]

    def w_subfields_by_value(self, value='_all'):
        return self.w_subfields.get(value, {})

    def w_data_json(self):
        return json.dumps(self.w_data, sort_keys=True)
