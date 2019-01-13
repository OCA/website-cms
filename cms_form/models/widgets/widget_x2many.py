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

    # TODO: rename all widget-specific methods like:
    #    `x2many_to_form` -> `_w_orm_to_form`
    #    `form_to_x2many` -> `_w_form_to_orm`
    # and make mixin's `w_load` and `w_extract` methods use them.
    # In this way we remove all the overrides on `w_load` and `w_extract`.
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
        ids = []
        if isinstance(value, type(self.w_comodel)):
            ids = value.ids
        elif isinstance(value, str):
            ids = self.w_ids_from_input(value)
        req_val = self.w_ids_from_input(req_values.get(self.w_fname, ''))
        if req_val:
            # request value take precedence
            ids = req_val[:]
        read_fields = [self.w_diplay_field, ]
        if 'name' in self.w_comodel:
            read_fields.append('name')
        return json.dumps(self.w_comodel.browse(ids).read(read_fields))

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
