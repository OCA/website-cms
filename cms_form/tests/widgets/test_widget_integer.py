# Copyright 2019 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from .common import TestWidgetCase, fake_form, fake_field


class TestWidgetInteger(TestWidgetCase):

    # TODO: test extraction and conversion to proper field value
    # on EVERY widget and not just rely on the marshallers.
    # Of course we have to switch to `w_html_fname` approach as hidden widget.
    # This implies that we test w/ a full request too.

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        form = fake_form(an_int_field=10)
        cls.w_name, cls.w_field = fake_field('an_int_field', type='integer')
        cls.widget = cls.get_widget(
            cls.w_name, cls.w_field,
            form=form, widget_model='cms.form.widget.integer')

    def test_widget_integer_input(self):
        expected_attrs = {
            'type': 'text',
            'id': 'an_int_field',
            'name': 'an_int_field',
            'placeholder': 'An int field...',
            'value': '10',
            'class': 'form-control ',
        }
        self._test_widget_attributes(self.widget, 'input', expected_attrs)

    def test_widget_integer_input_required(self):
        self.widget.w_field['required'] = True
        expected_attrs = {
            'type': 'text',
            'id': 'an_int_field',
            'name': 'an_int_field',
            'placeholder': 'An int field...',
            'value': '10',
            'class': 'form-control ',
            'required': '1',
        }
        self._test_widget_attributes(self.widget, 'input', expected_attrs)

    def test_widget_integer_input_extract(self):
        self.assertEqual(self.widget.w_extract(an_int_field='1'), 1)
        self.assertEqual(self.widget.w_extract(an_int_field='4'), 4)
        self.assertEqual(self.widget.w_extract(an_int_field='2.0'), None)
        self.assertEqual(self.widget.w_extract(an_int_field=''), None)
