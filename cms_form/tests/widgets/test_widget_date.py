# Copyright 2019 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import json
from .common import TestWidgetCase, fake_form, fake_field


class TestWidgetDate(TestWidgetCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = fake_form(a_date_field='2019-01-12', type='date')
        cls.w_name, cls.w_field = fake_field('a_date_field')
        cls.widget = cls.get_widget(
            cls.w_name, cls.w_field,
            form=cls.form, widget_model='cms.form.widget.date')

    def test_widget_date_input(self):
        node = self.to_xml_node(self.widget.render())[0]
        # we have 2 inputs, display one
        node_input_disp = self.find_input_name(node, self.w_name + '_display')
        self.assertEqual(len(node_input_disp), 1)
        expected_attrs = {
            'type': 'text',
            'id': 'a_date_field_display',
            'name': 'a_date_field_display',
            'class': 'form-control js_datepicker ',
            'placeholder': '',
        }
        self._test_element_attributes(
            node_input_disp[0], 'input', expected_attrs)

        # TODO: check on json params on other widgets too
        self.assertEqual(
            json.loads(node_input_disp[0].attrib['data-params']), {
                'defaultToday': True,
            }
        )
        # and the real one holding the value which is hidden
        node_input = self.find_input_name(node, self.w_name)
        self.assertEqual(len(node_input), 1)
        expected_attrs = {
            'type': 'hidden',
            'id': 'a_date_field',
            'name': 'a_date_field',
            'value': '2019-01-12',
        }
        self._test_element_attributes(node_input[0], 'input', expected_attrs)

    def test_widget_date_input_required(self):
        self.widget.w_field['required'] = True
        expected_attrs = {
            'type': 'text',
            'id': 'a_date_field_display',
            'name': 'a_date_field_display',
            'class': 'form-control js_datepicker ',
            'required': '1',
        }
        self._test_widget_attributes(self.widget, 'input', expected_attrs)

    def test_widget_date_input_custom_dp_attrs(self):
        widget = self.get_widget(
            self.w_name, self.w_field,
            form=self.form, widget_model='cms.form.widget.date',
            format='%m.%Y', placeholder='Custom',
        )
        self.assertEqual(widget.w_placeholder, 'Custom')
        self.assertEqual(
            widget.w_data_json(),
            '{"defaultToday": true, "dp": {"format": "%m.%Y"}}'
        )

    def test_widget_date_input_all_elems(self):
        node = self.to_xml_node(self.widget.render())[0]
        self._test_element_attributes(
            node, 'div', {'class': 'input-group'},
        )
        self.assertEqual(len(node.getchildren()), 3)
        self._test_element_attributes(
            node.getchildren()[0], 'input', {}
        )
        self._test_element_attributes(
            node.getchildren()[1], 'input',
            {'type': 'hidden'}
        )
        self._test_element_attributes(
            node.getchildren()[2], 'span',
            {'class': 'input-group-addon js_datepicker_trigger'}
        )
        self._test_element_attributes(
            node.getchildren()[2].getchildren()[0], 'span',
            {'class': 'fa fa-calendar'}
        )

    def test_widget_date_input_extract_default_format(self):
        self.assertEqual(self.widget.w_extract(a_date_field=''), None)
        self.assertEqual(
            self.widget.w_extract(a_date_field='2019-01-12'),
            '2019-01-12'
        )
