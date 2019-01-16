# Copyright 2019 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from .common import TestWidgetCase, fake_form, fake_field


class TestWidgetSelection(TestWidgetCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = fake_form(
            # fake defaults
            selection_char_field='opt1',
            selection_integer_field=2,
            selection_float_field=3.0,
        )

    def test_widget_selection_base(self):
        select_options = [
            ('opt1', 'Option 1'),
        ]
        w_name, w_field = fake_field(
            'selection_char_field',
            type='selection',
            selection=select_options,
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.selection')
        expected_attrs = {
            'id': 'selection_char_field',
            'name': 'selection_char_field',
        }
        self._test_widget_attributes(widget, 'select', expected_attrs)
        widget.w_field['required'] = True
        expected_attrs['required'] = '1'
        self._test_widget_attributes(widget, 'select', expected_attrs)

    def test_widget_selection_char(self):
        select_options = [
            ('opt1', 'Option 1'),
            ('opt2', 'Option 2'),
            ('opt3', 'Option 3'),
        ]
        w_name, w_field = fake_field(
            'selection_char_field',
            type='selection',
            selection=select_options,
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.selection')
        expected_attrs = {
            'id': 'selection_char_field',
            'name': 'selection_char_field',
        }
        node = self._test_widget_attributes(widget, 'select', expected_attrs)
        node_children = node.getchildren()
        self.assertEqual(len(node_children), 4)
        self.assertEqual(
            node_children[0].attrib, {'value': '', 'class': 'empty_item'})
        self.assertEqual(
            node_children[0].text.strip(), 'Selection char field...')
        for i in range(1, 4):
            expected_attrs = {'value': 'opt%s' % i}
            if i == 1:
                expected_attrs['selected'] = 'selected'
            self.assertEqual(
                node_children[i].attrib, expected_attrs)
            self.assertEqual(
                node_children[i].text.strip(), 'Option %s' % i)

        # test conversion
        extracted = widget.w_extract(selection_char_field='opt2')
        self.assertTrue(isinstance(extracted, str))

    def test_widget_selection_integer(self):
        select_options = [
            (1, 'Option 1'),
            (2, 'Option 2'),
            (3, 'Option 3'),
        ]
        w_name, w_field = fake_field(
            'selection_integer_field',
            type='selection',
            selection=select_options,
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.selection')
        expected_attrs = {
            'id': 'selection_integer_field',
            'name': 'selection_integer_field',
        }
        node = self._test_widget_attributes(widget, 'select', expected_attrs)
        node_children = node.getchildren()
        self.assertEqual(len(node_children), 4)
        self.assertEqual(
            node_children[0].attrib, {'value': '', 'class': 'empty_item'})
        self.assertEqual(
            node_children[0].text.strip(), 'Selection integer field...')
        for i in range(1, 4):
            expected_attrs = {'value': str(i)}
            if i == 2:
                expected_attrs['selected'] = 'selected'
            self.assertEqual(
                node_children[i].attrib, expected_attrs)
            self.assertEqual(
                node_children[i].text.strip(), 'Option %s' % i)

        # test conversion
        extracted = widget.w_extract(selection_integer_field='2')
        self.assertTrue(isinstance(extracted, int))

    def test_widget_selection_float(self):
        select_options = [
            (1.0, 'Option 1'),
            (2.0, 'Option 2'),
            (3.0, 'Option 3'),
        ]
        w_name, w_field = fake_field(
            'selection_float_field',
            type='selection',
            selection=select_options,
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.selection')
        expected_attrs = {
            'id': 'selection_float_field',
            'name': 'selection_float_field',
        }
        node = self._test_widget_attributes(widget, 'select', expected_attrs)
        node_children = node.getchildren()
        self.assertEqual(len(node_children), 4)
        self._test_element_attributes(
            node_children[0],
            'option',
            {'value': '', 'class': 'empty_item'},
            text='Selection float field...',
        )
        for i in range(1, 4):
            expected_attrs = {'value': '%s.0' % i}
            if i == 3:
                expected_attrs['selected'] = 'selected'
            self._test_element_attributes(
                node_children[i],
                'option',
                expected_attrs,
                text='Option %s' % i,
            )
        # test conversion
        extracted = widget.w_extract(selection_float_field='3.0')
        self.assertTrue(isinstance(extracted, float))

    def test_widget_selection_non_selection_field(self):
        w_name, w_field = fake_field(
            'selection_char_field',
            type='selection',
            # do not pass `selection`
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.selection')
        # no selection found: should not fail and give back an empty list
        self.assertEqual(widget.w_option_items, [])
