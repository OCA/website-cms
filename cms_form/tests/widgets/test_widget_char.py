# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from .common import TestWidgetCase, fake_form, fake_field


class TestWidgetChar(TestWidgetCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        form = fake_form(a_char_field='abc')
        cls.w_name, cls.w_field = fake_field('a_char_field')
        cls.widget = cls.get_widget(
            cls.w_name, cls.w_field,
            form=form, widget_model='cms.form.widget.char')

    def test_widget_char_input(self):
        node = self.to_xml_node(self.widget.render())[0]
        node_input = self.find_input_name(node, self.w_name)
        self.assertEqual(len(node_input), 1)
        expected_attrs = {
            'type': 'text',
            'name': 'a_char_field',
            'placeholder': 'A char field...',
            'value': 'abc',
            'class': 'form-control ',
        }
        for attr_name, attr_value in expected_attrs.items():
            self.assertEqual(node_input[0].attrib[attr_name], attr_value)
        self.assertNotIn('required', node_input[0].attrib)

    def test_widget_char_input_required(self):
        self.widget.w_field['required'] = True
        node = self.to_xml_node(self.widget.render())[0]
        node_input = self.find_input_name(node, self.w_name)
        self.assertEqual(len(node_input), 1)
        expected_attrs = {
            'type': 'text',
            'name': 'a_char_field',
            'placeholder': 'A char field...',
            'value': 'abc',
            'class': 'form-control ',
            'required': '1',
        }
        for attr_name, attr_value in expected_attrs.items():
            self.assertEqual(node_input[0].attrib[attr_name], attr_value)
