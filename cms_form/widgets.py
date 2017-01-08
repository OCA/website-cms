# -*- coding: utf-8 -*-
# Copyright 2016 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


class Widget(object):
    key = ''
    css_klass = ''
    data = {}

    def __init__(self, form, fname, field):
        self.form = form
        self.fname = fname
        self.field = field
        self.env = form.env

    def render(self):
        values = self.form.form_render_values
        values['widget'] = self
        return self.env.ref(self.key).render(values)


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
}
