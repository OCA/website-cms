# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from .common import FormRenderTestCase
from .fake_models import FakeFieldsForm


class TestRender(FormRenderTestCase):

    TEST_MODELS_KLASSES = [FakeFieldsForm, ]

    @classmethod
    def setUpClass(cls):
        super(TestRender, cls).setUpClass()
        cls._setup_models()

    @classmethod
    def tearDownClass(cls):
        cls._teardown_models()
        super(TestRender, cls).tearDownClass()

    def test_render_form_attrs(self):
        form = self.get_form('cms.form.test_fields')
        html = form.form_render()
        node = self.to_xml_node(html)[0]
        self.assertEqual(node.tag, 'form')
        expected_attrs = {
            'enctype': 'multipart/form-data',
            'method': 'POST',
            'class': 'form-horizontal'
        }
        self.assert_match_attrs(node.attrib, expected_attrs)

    def test_render_form_fields(self):
        form = self.get_form('cms.form.test_fields')
        html = form.form_render()
        node = self.to_xml_node(html)[0]
        expected_fields = (
            'csrf_token',
            'a_char',
            'a_float',
            'a_number',
            'a_many2one',
            'a_many2many',
            'a_one2many',
        )
        self.assertEqual(
            len(node[0].xpath('//input|//select')), len(expected_fields)
        )
        self.assert_match_inputs(node, expected_fields)

    def test_field_attrs(self):
        # TODO: test all fields rendering
        pass
