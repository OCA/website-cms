# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from .common import TestWidgetCase, fake_form, fake_field


TXT = """Lorem ipsum dolor sit amet, mea te propriae verterem.
Soluta viderer no vis. Ut populo suscipit vel.
Usu ea timeam utamur consectetuer, no simul dolorum vel.
Duo illum dolore id, ea mei error gloriatur voluptaria."""


class TestWidgetTxt(TestWidgetCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = fake_form(
            a_char_field='Just a string',
            a_text_field=TXT,
        )

    def test_widget_char_input(self):
        w_name, w_field = fake_field('a_char_field')
        widget = self.get_widget(
            w_name, w_field,
            form=self.form, widget_model='cms.form.widget.char')
        expected_attrs = {
            'type': 'text',
            'id': 'a_char_field',
            'name': 'a_char_field',
            'placeholder': 'A char field...',
            'value': 'Just a string',
            'class': 'form-control ',
        }
        self._test_widget_attributes(widget, 'input', expected_attrs)
        widget.w_field['required'] = True
        expected_attrs['required'] = '1'
        self._test_widget_attributes(widget, 'input', expected_attrs)

    def test_widget_text_input(self):
        w_name, w_field = fake_field('a_text_field', type='text')
        widget = self.get_widget(
            w_name, w_field,
            form=self.form, widget_model='cms.form.widget.text')
        expected_attrs = {
            'id': 'a_text_field',
            'name': 'a_text_field',
            'class': 'form-control ',
        }
        self._test_widget_attributes(
            widget, 'textarea', expected_attrs, text=TXT)
        widget.w_field['required'] = True
        expected_attrs['required'] = '1'
        self._test_widget_attributes(
            widget, 'textarea', expected_attrs, text=TXT)

    def test_widget_text_input_maxlength(self):
        w_name, w_field = fake_field(
            'a_text_field', type='text', maxlength=100)
        widget = self.get_widget(
            w_name, w_field,
            form=self.form, widget_model='cms.form.widget.text')
        node_items = self.to_xml_node(widget.render())
        self.assertEqual(len(node_items), 2)
        node_textarea = node_items[0]
        expected_attrs = {
            'id': 'a_text_field',
            'name': 'a_text_field',
            'class': 'form-control ',
            'maxlength': '100',
        }
        self._test_element_attributes(
            node_textarea, 'textarea', expected_attrs, text=TXT,
        )
        node_counter = node_items[1]
        expected_attrs = {
            'type': 'text',
            'id': 'a_text_field_counter',
            'name': 'a_text_field_counter',
            'size': '3',
            'class': 'form-control text-counter',
        }
        self._test_element_attributes(
            node_counter, 'input', expected_attrs,
        )
