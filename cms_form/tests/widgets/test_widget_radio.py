# Copyright 2019 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from .common import TestWidgetCase, fake_form, fake_field


class TestWidgetRadio(TestWidgetCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = fake_form(
            # fake defaults
            radio_field='opt2',
        )

    def test_widget_radio_base(self):
        select_options = [
            ('opt1', 'Option 1'),
            ('opt2', 'Option 2'),
            ('opt3', 'Option 3'),
        ]
        w_name, w_field = fake_field(
            'radio_field',
            type='selection',
            selection=select_options,
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.radio')
        node = self.to_xml_node(widget.render())[0]
        self.assertIn('radio-select', node.attrib['class'])
        # we have only 3 options
        self.assertEqual(len(node.getchildren()), 3)
        for i, node_option in enumerate(node.getchildren()):
            self._test_element_attributes(
                node_option, 'div', {'class': 'radio option-item'}
            )
            # we should have only the label wrapping the input
            self.assertEqual(len(node_option.getchildren()), 1)
            node_label = node_option.getchildren()[0]
            self._test_element_attributes(
                node_label, 'label', {'for': 'radio_field_%s' % i}
            )
            # we should have only the input and the span w/ text here
            self.assertEqual(len(node_label.getchildren()), 2)
            node_input = node_label.getchildren()[0]
            expected_attrs = {
                'type': 'radio',
                'name': 'radio_field',
                'id': 'radio_field_%s' % i,
                'value': 'opt%s' % (i + 1),
            }
            if i == 1:
                expected_attrs['checked'] = 'checked'
            self._test_element_attributes(
                node_input, 'input', expected_attrs,
            )
            node_span = node_label.getchildren()[1]
            self._test_element_attributes(
                node_span, 'span', {}, text='Option %s' % (i + 1),
            )
