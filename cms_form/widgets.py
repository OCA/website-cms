# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .utils import TRUE_VALUES

# TODO: should we make widget abstract models?
# It might be worth to add a `cms.form.widget` base klass
# and define one klass per each kind of widget
# as ir.qweb does for rendering fields.


class Widget(object):
    key = ''
    css_klass = ''

    def __init__(self, form, fname, field, data=None):
        self.form = form
        self.form_values = form.form_render_values
        self.fname = fname
        self.field = field
        self.field_value = self.form_values.get('form_data', {}).get(fname)
        self.env = form.env
        self.data = data or {}

    def render(self):
        return self.env.ref(self.key).render({'widget': self})


class CharWidget(Widget):
    key = 'cms_form.field_widget_char'


class M2OWidget(Widget):
    key = 'cms_form.field_widget_m2o'

    def __init__(self, form, fname, field, data=None):
        super(M2OWidget, self).__init__(form, fname, field, data=data)
        self.comodel = self.env[self.field['relation']]
        self.domain = self.field.get('domain', [])

    @property
    def option_items(self):
        return self.comodel.search(self.domain)


class SelectionWidget(Widget):
    key = 'cms_form.field_widget_selection'

    @property
    def option_items(self):
        return [
            {'value': x[0], 'label': x[1]}
            for x in self.field['selection']
        ]


class X2MWidget(Widget):
    key = 'cms_form.field_widget_x2m'


class DateWidget(Widget):
    key = 'cms_form.field_widget_date'


class TextWidget(Widget):
    key = 'cms_form.field_widget_text'

    def __init__(self, form, fname, field, data=None, maxlength=None):
        super(TextWidget, self).__init__(
            form, fname, field, data=data
        )
        self.maxlength = maxlength


class ImageWidget(Widget):
    key = 'cms_form.field_widget_image'


class BooleanWidget(Widget):
    key = 'cms_form.field_widget_boolean'

    def __init__(self, form, fname, field, data=None):
        super(BooleanWidget, self).__init__(form, fname, field, data=data)
        self.field_value = self.field_value in TRUE_VALUES


DEFAULT_WIDGETS = {
    'many2one': M2OWidget,
    'one2many': X2MWidget,
    'many2many': X2MWidget,
    'date': DateWidget,
    'text': TextWidget,
    # TODO: we expect an image field to be named "image"
    # but we should handle normal file fields and image fields properly.
    # We should have an 'image' field type...
    'image': ImageWidget,
    'boolean': BooleanWidget,
    'selection': SelectionWidget,
}
