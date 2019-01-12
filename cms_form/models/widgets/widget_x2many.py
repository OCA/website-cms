# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import json
from odoo import models


class X2MWidget(models.AbstractModel):
    _name = 'cms.form.widget.x2m.mixin'
    _inherit = 'cms.form.widget.mixin'
    _w_template = 'cms_form.field_widget_x2m'
    w_diplay_field = 'display_name'

    def widget_init(self, form, fname, field, **kw):
        widget = super().widget_init(form, fname, field, **kw)
        widget.w_comodel = self.env[widget.w_field['relation']]
        widget.w_domain = widget.w_field.get('domain', [])
        return widget

    def w_load(self, **req_values):
        value = super().w_load(**req_values)
        return self.x2many_to_form(value, **req_values)

    def _is_not_valued(self, value):
        if not value:
            return True
        if isinstance(value, (list, tuple)):
            # if value comes from `default_get` we have [(6, 0, [])]
            if not all([x[-1] for x in value]):
                return True
        return False

    def x2many_to_form(self, value, **req_values):
        if self._is_not_valued(value):
            return json.dumps([])
        if not isinstance(value, str) \
                and self.w_record and self.w_record[self.w_fname] == value:
            # value from record
            value = [
                {'id': x.id, 'name': x[self.w_diplay_field]}
                for x in value or []
            ]
        elif isinstance(value, str) and value == req_values.get(self.w_fname):
            # value from request
            # FIXME: the field could come from the form not the model!
            value = self.w_form_model[self.w_fname].browse(
                self.w_ids_from_input(value)).read(['name'])
        value = json.dumps(value)
        return value

    def w_extract(self, **req_values):
        value = super().w_extract(**req_values)
        return self.form_to_x2many(value, **req_values)

    def form_to_x2many(self, value, **req_values):
        _value = False
        if self.w_form._form_extract_value_mode == 'write':
            if value:
                _value = [(6, False, self.w_ids_from_input(value))]
            else:
                # wipe them
                _value = [(5, )]
        else:
            _value = value and self.w_ids_from_input(value) or []
        return _value


# TODO: handle advanced editing via table view and subform for such fields
class O2ManyWidget(models.AbstractModel):
    _name = 'cms.form.widget.one2many'
    _inherit = 'cms.form.widget.x2m.mixin'


class M2MWidget(models.AbstractModel):
    _name = 'cms.form.widget.many2many'
    _inherit = 'cms.form.widget.x2m.mixin'
