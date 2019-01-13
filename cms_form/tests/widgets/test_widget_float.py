# Copyright 2019 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from .common import TestWidgetCase, fake_form, fake_field


class TestWidgetFloat(TestWidgetCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        form = fake_form(a_float_field=2.0)
        cls.w_name, cls.w_field = fake_field('a_float_field', type='float')
        cls.widget = cls.get_widget(
            cls.w_name, cls.w_field,
            form=form, widget_model='cms.form.widget.float')

    def test_widget_float_input(self):
        node = self.to_xml_node(self.widget.render())[0]
        node_input = self.find_input_name(node, self.w_name)
        self.assertEqual(len(node_input), 1)
        expected_attrs = {
            'type': 'text',
            'id': 'a_float_field',
            'name': 'a_float_field',
            'placeholder': 'A float field...',
            'value': '2.0',
            'class': 'form-control ',
        }
        for attr_name, attr_value in expected_attrs.items():
            self.assertEqual(node_input[0].attrib[attr_name], attr_value)
        self.assertNotIn('required', node_input[0].attrib)

    def test_widget_float_input_required(self):
        self.widget.w_field['required'] = True
        node = self.to_xml_node(self.widget.render())[0]
        node_input = self.find_input_name(node, self.w_name)
        self.assertEqual(len(node_input), 1)
        expected_attrs = {
            'type': 'text',
            'id': 'a_float_field',
            'name': 'a_float_field',
            'placeholder': 'A float field...',
            'value': '2.0',
            'class': 'form-control ',
            'required': '1',
        }
        for attr_name, attr_value in expected_attrs.items():
            self.assertEqual(node_input[0].attrib[attr_name], attr_value)

    def test_widget_float_input_extract(self):
        self.assertEqual(self.widget.w_extract(a_float_field='1'), 1.0)
        self.assertEqual(self.widget.w_extract(a_float_field='2.0'), 2.0)
        self.assertEqual(self.widget.w_extract(a_float_field='2,0'), None)
        self.assertEqual(self.widget.w_extract(a_float_field=''), None)
