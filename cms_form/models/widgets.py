# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import json
import werkzeug
import base64

from odoo.tools.mimetypes import guess_mimetype
from odoo import models

from .. import utils


class Widget(models.AbstractModel):
    _name = 'cms.form.widget.mixin'

    # use `w_` prefix as a namespace for all widget properties
    _w_template = ''
    _w_css_klass = ''

    def widget_init(self, form, fname, field,
                    data=None, subfields=None, template='', css_klass=''):
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
        # we could have form-only fields (like `custom` in test form below)
        if self.w_record and self.w_fname in self.w_record:
            value = self.w_record[self.w_fname] or value
        # maybe a POST request with new values: override item value
        value = req_values.get(self.w_fname, value)
        return value

    def w_extract(self, **req_values):
        """Extract value from form submit."""
        return req_values.get(self.w_fname)

    @staticmethod
    def w_ids_from_input(value):
        """Convert list of ids from form input."""
        return [int(rec_id.strip())
                for rec_id in value.split(',') if rec_id.strip().isdigit()]

    def w_subfields_by_value(self, value='_all'):
        return self.w_subfields.get(value, {})

    def w_data_json(self):
        return json.dumps(self.w_data)


class CharWidget(models.AbstractModel):
    _name = 'cms.form.widget.char'
    _inherit = 'cms.form.widget.mixin'
    _w_template = 'cms_form.field_widget_char'


class HiddenWidget(models.AbstractModel):
    _name = 'cms.form.widget.hidden'
    _inherit = 'cms.form.widget.mixin'
    _w_template = 'cms_form.field_widget_hidden'

    @property
    def w_html_fname(self):
        """Field name for final HTML markup."""
        marshaller = ''
        if self.w_field['type'] in ('many2one', 'integer'):
            marshaller = ':int'
        elif self.w_field['type'] in ('float', ):
            marshaller = ':float'
        elif self.w_field['type'] == 'selection' and self.w_field['selection']:
            first_value = self.w_field['selection'][0][0]
            # fields.Selection does the same check to determine PG col type
            if isinstance(first_value, int):
                marshaller = ':int'
            elif isinstance(first_value, float):
                marshaller = ':float'
        return self.w_fname + marshaller


class IntegerWidget(models.AbstractModel):
    _name = 'cms.form.widget.integer'
    _inherit = 'cms.form.widget.char'

    def w_extract(self, **req_values):
        value = super().w_extract(**req_values)
        return utils.safe_to_integer(value)


class FloatWidget(models.AbstractModel):
    _name = 'cms.form.widget.float'
    _inherit = 'cms.form.widget.char'

    def w_extract(self, **req_values):
        value = super().w_extract(**req_values)
        return utils.safe_to_float(value)


class M2OWidget(models.AbstractModel):
    _name = 'cms.form.widget.many2one'
    _inherit = 'cms.form.widget.mixin'
    _w_template = 'cms_form.field_widget_m2o'

    def widget_init(self, form, fname, field, **kw):
        widget = super().widget_init(form, fname, field, **kw)
        widget.w_comodel = self.env[widget.w_field['relation']]
        widget.w_domain = widget.w_field.get('domain', [])
        return widget

    @property
    def w_option_items(self):
        return self.w_comodel.search(self.w_domain)

    def w_load(self, **req_values):
        value = super().w_load(**req_values)
        return self.m2o_to_form(value, **req_values)

    def m2o_to_form(self, value, **req_values):
        # important: return False if no value
        # otherwise you will compare an empty recordset with an id
        # in a select input in form widget template.
        if isinstance(value, str) and value.isdigit():
            # number as string
            return int(value) > 0 and int(value)
        elif isinstance(value, models.BaseModel):
            return value and value.id or None
        elif isinstance(value, int):
            return value
        return None

    def w_extract(self, **req_values):
        value = super().w_extract(**req_values)
        return self.form_to_m2o(value, **req_values)

    def form_to_m2o(self, value, **req_values):
        val = utils.safe_to_integer(value) or 0
        # we don't want m2o value do be < 1
        return val > 0 and val or None


class M2OMultiWidget(models.AbstractModel):
    _name = 'cms.form.widget.many2one.multi'
    _inherit = 'cms.form.widget.many2one'
    _w_template = 'cms_form.field_widget_m2o_multi'
    w_diplay_field = 'display_name'

    def m2o_to_form(self, value, **req_values):
        if not value:
            return json.dumps([])
        if (isinstance(value, str) and
                value == req_values.get(self.w_fname)):
            value = self.w_comodel.browse(
                self.w_ids_from_input(value)).read(['name'])
        value = json.dumps(value)
        return value

    def form_to_m2o(self, value, **req_values):
        return self.w_ids_from_input(value) if value else None


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
        if self.w_field['selection']:
            # `fields.Selection` does this under the hood
            # to state the PG column type to be used.
            first_value = self.w_field['selection'][0][0]
        # fields.Selection does the same check to determine PG col type
        if isinstance(first_value, int) and value:
            value = int(value)
        return value

    @property
    def w_option_items(self):
        return [
            {'value': x[0], 'label': x[1]}
            for x in self.w_field['selection']
        ]


class RadioSelectionWidget(SelectionWidget):
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
        if (not isinstance(value, str) and
                self.w_record and self.w_record[self.w_fname] == value):
            # value from record
            value = [
                {'id': x.id, 'name': x[self.w_diplay_field]}
                for x in value or []
            ]
        elif (isinstance(value, str) and
                value == req_values.get(self.w_fname)):
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


# TODO: add datetime widget
class DateWidget(models.AbstractModel):
    _name = 'cms.form.widget.date'
    _inherit = 'cms.form.widget.mixin'
    _w_template = 'cms_form.field_widget_date'

    def widget_init(self, form, fname, field, **kw):
        widget = super().widget_init(form, fname, field, **kw)
        if 'defaultToday' not in widget.w_data:
            # set today's date by default
            widget.w_data['defaultToday'] = True
        return widget

    def w_extract(self, **req_values):
        value = super().w_extract(**req_values)
        return self.form_to_date(value, **req_values)

    def form_to_date(self, value, **req_values):
        return utils.safe_to_date(value)


class TextWidget(models.AbstractModel):
    _name = 'cms.form.widget.text'
    _inherit = 'cms.form.widget.mixin'
    _w_template = 'cms_form.field_widget_text'
    w_maxlength = None

    def widget_init(self, form, fname, field, **kw):
        widget = super().widget_init(
            form, fname, field, **kw
        )
        widget.w_maxlength = kw.get('maxlength')
        return widget


class BinaryWidget(models.AbstractModel):
    _name = 'cms.form.widget.binary.mixin'
    _inherit = 'cms.form.widget.mixin'

    def w_load(self, **req_values):
        value = super().w_load(**req_values)
        return self.binary_to_form(value, **req_values)

    def binary_to_form(self, value, **req_values):
        _value = {
            # 'value': '',
            # 'raw_value': '',
            # 'mimetype': '',
        }
        if value:
            if isinstance(value, werkzeug.datastructures.FileStorage):
                # value from request, we cannot set a value for input field
                value = ''
                mimetype = ''
            else:
                value = str(value, 'utf-8')
                mimetype = guess_mimetype(base64.b64decode(value))
            _value = {
                'value': value,
                'raw_value': value,
                'mimetype': mimetype,
            }
            if mimetype.startswith('image/'):
                _value['value'] = 'data:{};base64,{}'.format(mimetype, value)
        return _value

    def w_extract(self, **req_values):
        value = super().w_extract(**req_values)
        return self.form_to_binary(value, **req_values)

    def form_to_binary(self, value, **req_values):
        _value = False
        if req_values.get(self.w_fname + '_keepcheck') == 'yes':
            # prevent discarding image
            req_values.pop(self.w_fname, None)
            req_values.pop(self.w_fname + '_keepcheck')
            return None
        if value:
            if hasattr(value, 'read'):
                file_content = value.read()
                _value = base64.encodestring(file_content)
            else:
                _value = value.split(',')[-1]
        return _value


class ImageWidget(models.AbstractModel):
    _name = 'cms.form.widget.image'
    _inherit = 'cms.form.widget.binary.mixin'
    _w_template = 'cms_form.field_widget_image'


class BooleanWidget(models.AbstractModel):
    _name = 'cms.form.widget.boolean'
    _inherit = 'cms.form.widget.mixin'
    _w_template = 'cms_form.field_widget_boolean'

    w_true_values = utils.TRUE_VALUES

    def widget_init(self, form, fname, field, **kw):
        widget = super().widget_init(
            form, fname, field, **kw)
        widget.w_true_values = kw.get('true_values', self.w_true_values)
        widget.w_field_value = widget.w_field_value in self.w_true_values
        return widget

    def w_extract(self, **req_values):
        value = super().w_extract(**req_values)
        return utils.string_to_bool(value, true_values=self.w_true_values)
