# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


# TODO: should we make widget abstract models?
# It might be worth to add a `cms.form.widget` base klass
# and define one klass per each kind of widget
# as ir.qweb does for rendering fields.

class Widget(object):
    key = ''
    css_klass = ''
    data = {}

    def __init__(self, form, fname, field):
        self.form = form
        self.form_values = form.form_render_values
        self.fname = fname
        self.field = field
        self.field_value = self.form_values.get('form_data', {}).get(fname)
        self.env = form.env

    def render(self):
        return self.env.ref(self.key).render({'widget': self})


class CharWidget(Widget):
    key = 'cms_form.field_widget_char'


class M2OWidget(Widget):
    key = 'cms_form.field_widget_m2o'


class X2MWidget(Widget):
    key = 'cms_form.field_widget_x2m'


class DateWidget(Widget):
    key = 'cms_form.field_widget_date'


class TextWidget(Widget):
    key = 'cms_form.field_widget_text'


class ImageWidget(Widget):
    key = 'cms_form.field_widget_image'


class BooleanWidget(Widget):
    key = 'cms_form.field_widget_boolean'


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
}
