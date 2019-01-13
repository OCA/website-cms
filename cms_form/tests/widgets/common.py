# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.tests.common import SavepointCase
import mock

from ..common import HTMLRenderMixin


def fake_form(main_object=None, **data):
    """Get a mocked fake form.

    :param data: kw args for setting form values
    """
    form = mock.MagicMock(name='FakeForm')
    form_values = mock.PropertyMock(return_value={'form_data': data})
    type(form).form_render_values = form_values
    form.main_object = main_object
    return form


def fake_field(name, **kw):
    """Get fake field specs `form_fields` compliant.

    :param name: field name
    :param kw: kw args to override some values
    """
    info = {
        'type': 'char',
        'required': False,
        'string': name.capitalize().replace('_', ' '),
        'readonly': False,
        'help': 'Help for %s' % name,
    }
    info.update(kw)
    return name, info


def get_widget(env, fname, field, form=None, widget_model=None, **kw):
    """Retrieve and initialize widget.

    :param fname: field name
    :param field: field info matching `form_fields` schema
    :param form: an instance of a cms_form
    :param widget_model: if you don't pass a form you must pass a w model
    """
    assert form or widget_model
    if not form:
        form = fake_form()
    if not widget_model:
        widget_model = form.form_get_widget_model(fname, field)
    return env[widget_model].widget_init(
        form, fname, field, **kw
    )


class TestWidgetCase(SavepointCase, HTMLRenderMixin):

    at_install = False
    post_install = True

    @classmethod
    def get_widget(cls, fname, field, **kw):
        return get_widget(cls.env, fname, field, **kw)

    def _test_widget_attributes(self, widget, tag, expected, text=None):
        node = self.to_xml_node(widget.render())[0]
        node_input = self.find_input_name(node, expected['name'])
        self.assertEqual(len(node_input), 1)
        node_input = node_input[0]
        self._test_element_attributes(node_input, tag, expected, text=text)
        # return node for further testing
        return node_input

    def _test_element_attributes(self, node, tag, expected, text=None):
        self.assertEqual(node.tag, tag)
        for attr_name, attr_value in expected.items():
            self.assertEqual(node.attrib[attr_name], attr_value)
        # special attrs that should be set or not completely
        for attr_name in ('required', 'checked'):
            if expected.get(attr_name):
                self.assertIn(attr_name, node.attrib)
            else:
                self.assertNotIn(attr_name, node.attrib)
        if text:
            self.assertEqual(node.text.strip(), text)
