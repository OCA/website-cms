# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.addons.cms_form.tests.widgets.common import (
    TestWidgetCase,
    fake_form,
    fake_field,
)


class TestWidget(TestWidgetCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        form = fake_form()
        w_name, w_field = fake_field(
            'notification_type',
            type='selection',
            selection=[
                ('inbox', 'Inbox'),
                ('email', 'Email'),
            ]
        )
        cls.widget = cls.get_widget(
            w_name, w_field, form=form,
            widget_model='cms.form.widget.notif_radio')

    def test_default_templates(self):
        # the widget is fault tolerant if no help templates are found
        # since you may won't to drop them.
        for notif_type in ('email', 'inbox'):
            self.assertTrue(
                self.env.ref(self.widget.help_tmpl_prefix + notif_type)
            )

    def _test_option(self, node, attrs):
        for attr_name, attr_value in attrs.items():
            self.assertEqual(node.attrib[attr_name], attr_value)
        self.assertNotIn('required', node.attrib)
        node_wrapper = node.xpath(
            "ancestor::div[contains(@class, 'option-item')]")
        self.assertEqual(len(node_wrapper), 1)
        self.assertTrue(node_wrapper[0].xpath('//div[@class="help-block"]'))

    def test_widget_render(self):
        node = self.to_xml_node(self.widget.render())[0]
        node_input = self.find_input_name(node, 'notification_type')
        # it's radio widget, w/ 2 options
        self.assertEqual(len(node_input), 2)
        # check option 1
        expected_attrs = {
            'type': 'radio',
            'name': 'notification_type',
            'value': 'inbox',
            'id': 'notification_type_0',
        }
        self._test_option(node_input[0], expected_attrs)
        # check option 2
        expected_attrs = {
            'type': 'radio',
            'name': 'notification_type',
            'value': 'email',
            'id': 'notification_type_1',
        }
        self._test_option(node_input[1], expected_attrs)
