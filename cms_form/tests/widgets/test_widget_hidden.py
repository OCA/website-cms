# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from .common import TestWidgetCase, fake_form, fake_field


class TestWidgetHidden(TestWidgetCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = fake_form(
            # fake defaults
            char_field='abc',
            int_field=5,
            float_field=5.0,
            selection_str_field='1',
            selection_integer_field=2,
            selection_float_field=4.0,
            many2one_field=10,
        )

    def test_widget_char_input_hidden(self):
        """Test char field hidden."""
        w_name, w_field = fake_field('char_field')
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.hidden')
        expected_attrs = {
            'type': 'hidden',
            'id': 'char_field',
            'name': 'char_field',
            'value': 'abc',
        }
        self._test_widget_attributes(widget, 'input', expected_attrs)
        # make it required
        # we'll test this only here: behavior is the same for each field type
        widget.w_field['required'] = True
        expected_attrs['required'] = '1'
        self._test_widget_attributes(widget, 'input', expected_attrs)

    def test_widget_integer_input_hidden(self):
        """Test int field hidden."""
        w_name, w_field = fake_field('int_field', type='integer')
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.hidden')
        expected_attrs = {
            'type': 'hidden',
            'id': 'int_field',
            'name': 'int_field:int',
            'value': '5',
        }
        self._test_widget_attributes(widget, 'input', expected_attrs)

    def test_widget_float_input_hidden(self):
        """Test float field hidden."""
        w_name, w_field = fake_field('float_field', type='float')
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.hidden')
        expected_attrs = {
            'type': 'hidden',
            'id': 'float_field',
            'name': 'float_field:float',
            'value': '5.0',
        }
        self._test_widget_attributes(widget, 'input', expected_attrs)

    def test_widget_selection_string_input_hidden(self):
        """Test selection field hidden with string values."""
        w_name, w_field = fake_field(
            'selection_str_field',
            type='selection',
            selection=[('1', 'A'), ('2', 'B')])
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.hidden')
        expected_attrs = {
            'type': 'hidden',
            'id': 'selection_str_field',
            'name': 'selection_str_field',
            'value': '1',
        }
        self._test_widget_attributes(widget, 'input', expected_attrs)

    def test_widget_selection_integer_input_hidden(self):
        """Test selection field hidden with integer values."""
        w_name, w_field = fake_field(
            'selection_integer_field',
            type='selection',
            selection=[(1, 'A'), (2, 'B')])
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.hidden')
        expected_attrs = {
            'type': 'hidden',
            'id': 'selection_integer_field',
            'name': 'selection_integer_field:int',
            'value': '2',
        }
        self._test_widget_attributes(widget, 'input', expected_attrs)

    def test_widget_selection_float_input_hidden(self):
        """Test selection field hidden with float values."""
        w_name, w_field = fake_field(
            'selection_float_field',
            type='selection',
            selection=[(4.0, 'A'), (8.0, 'B')])
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.hidden')
        expected_attrs = {
            'type': 'hidden',
            'id': 'selection_float_field',
            'name': 'selection_float_field:float',
            'value': '4.0',
        }
        self._test_widget_attributes(widget, 'input', expected_attrs)

    def test_widget_many2one_input_hidden(self):
        """Test many2one field hidden."""
        w_name, w_field = fake_field('many2one_field', type='many2one')
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.hidden')
        expected_attrs = {
            'type': 'hidden',
            'id': 'many2one_field',
            'name': 'many2one_field:int',
            'value': '10',
        }
        self._test_widget_attributes(widget, 'input', expected_attrs)
