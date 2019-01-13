# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from .common import TestWidgetCase, fake_form, fake_field


class TestWidgetBoolean(TestWidgetCase):

    def _get_widget(self, field_value=False):
        """Initialize form w/ given value and return the widget."""
        form = fake_form(a_boolean_field=field_value)
        w_name, w_field = fake_field(
            'a_boolean_field',
            type='boolean',
        )
        return self.get_widget(
            w_name, w_field, form=form,
            widget_model='cms.form.widget.boolean')

    def test_widget_boolean_input(self):
        widget = self._get_widget()
        self.assertFalse(widget.w_field_value)
        expected_attrs = {
            'type': 'checkbox',
            'id': 'a_boolean_field',
            'name': 'a_boolean_field',
            'class': 'form-control ',
        }
        self._test_widget_attributes(widget, 'input', expected_attrs)

    def test_widget_boolean_input_required(self):
        widget = self._get_widget()
        self.assertFalse(widget.w_field_value)
        widget.w_field['required'] = True
        expected_attrs = {
            'type': 'checkbox',
            'id': 'a_boolean_field',
            'name': 'a_boolean_field',
            'class': 'form-control ',
            'required': '1',
        }
        self._test_widget_attributes(widget, 'input', expected_attrs)

    def test_widget_boolean_input_checked(self):
        widget = self._get_widget(field_value=True)
        self.assertTrue(widget.w_field_value)
        expected_attrs = {
            'type': 'checkbox',
            'id': 'a_boolean_field',
            'name': 'a_boolean_field',
            'class': 'form-control ',
            'checked': 'checked',
        }
        self._test_widget_attributes(widget, 'input', expected_attrs)

    def test_widget_boolean_input_extract(self):
        widget = self._get_widget()
        self.assertIs(widget.w_extract(a_boolean_field='1'), True)
        self.assertIs(widget.w_extract(a_boolean_field='ok'), True)
        self.assertIs(widget.w_extract(a_boolean_field='true'), True)
        self.assertIs(widget.w_extract(a_boolean_field='yes'), True)
        self.assertIs(widget.w_extract(a_boolean_field=True), True)
        self.assertIs(widget.w_extract(a_boolean_field=1), True)
        # any other value give us False
        self.assertIs(widget.w_extract(a_boolean_field=''), False)
        self.assertIs(widget.w_extract(a_boolean_field='no'), False)
