# Copyright 2019 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from .common import TestWidgetCase, fake_form, fake_field


class TestWidgetDate(TestWidgetCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        form = fake_form(a_date_field='2019-01-12', type='date')
        cls.w_name, cls.w_field = fake_field('a_date_field')
        cls.widget = cls.get_widget(
            cls.w_name, cls.w_field,
            form=form, widget_model='cms.form.widget.date')

    def test_widget_date_input(self):
        expected_attrs = {
            'type': 'text',
            'id': 'a_date_field',
            'name': 'a_date_field',
            'placeholder': 'YYYY-MM-DD',
            'value': '2019-01-12',
            'data-format': 'yy-mm-dd',
            'class': 'form-control js_datepicker ',
        }
        self._test_widget_attributes(self.widget, 'input', expected_attrs)

    def test_widget_date_input_required(self):
        self.widget.w_field['required'] = True
        expected_attrs = {
            'type': 'text',
            'id': 'a_date_field',
            'name': 'a_date_field',
            'placeholder': 'YYYY-MM-DD',
            'value': '2019-01-12',
            'data-format': 'yy-mm-dd',
            'class': 'form-control js_datepicker ',
            'required': '1',
        }
        self._test_widget_attributes(self.widget, 'input', expected_attrs)

    def test_widget_date_input_all_elems(self):
        node = self.to_xml_node(self.widget.render())[0]
        self._test_element_attributes(
            node, 'div', {'class': 'input-group'},
        )
        self.assertEqual(len(node.getchildren()), 2)
        self._test_element_attributes(
            node.getchildren()[0], 'input', {}
        )
        self._test_element_attributes(
            node.getchildren()[1], 'span',
            {'class': 'input-group-addon js_datepicker_trigger'}
        )
        self._test_element_attributes(
            node.getchildren()[1].getchildren()[0], 'span',
            {'class': 'fa fa-calendar'}
        )

    def test_widget_date_input_extract(self):
        self.assertEqual(self.widget.w_extract(a_date_field=''), None)
        self.assertEqual(
            self.widget.w_extract(a_date_field='2019-01-12'), '2019-01-12')
