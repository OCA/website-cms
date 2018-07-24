# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from .common import FormRenderTestCase
from .fake_models import FakeFieldsForm, FakeFieldsFormWithFieldsets


class TestRender(FormRenderTestCase):

    TEST_MODELS_KLASSES = [FakeFieldsForm, FakeFieldsFormWithFieldsets]

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
        # all fields are rendered
        self.assertEqual(
            len(node[0].xpath('//input|//select')), len(expected_fields)
        )
        self.assert_match_inputs(node, expected_fields)

    def test_field_wrapper_attrs(self):
        form = self.get_form('cms.form.test_fields')
        form_fields = form.form_fields()
        html = form.form_render()
        node = self.to_xml_node(html)[0]
        expected_fields = (
            'a_char',
            'a_float',
            'a_number',
            'a_many2one',
            'a_many2many',
            'a_one2many',
        )
        for fname in expected_fields:
            fnode = self.find_input_name(node, fname)[0]
            # catch 2nd one since the 1st is the main `form-fields` wrapper
            fwrapper = fnode.xpath(
                "ancestor::div[contains(@class, 'form-field')]")[1]
            self.assertEqual(
                fwrapper.attrib['class'],
                form.form_make_field_wrapper_klass(fname, form_fields[fname])
            )

    def test_render_form_fieldsets(self):
        form = self.get_form('cms.form.test_fieldsets')
        html = form.form_render()
        node = self.to_xml_node(html)[0]
        # we still get all the fields
        expected_fields = (
            'csrf_token',
            'a_char',
            'ihaveagroup',
            'a_float',
            'a_number',
            'a_many2one',
            'a_many2many',
            'a_one2many',
        )
        # all fields are rendered
        self.assertEqual(
            len(node[0].xpath('//input|//select')), len(expected_fields)
        )
        self.assert_match_inputs(node, expected_fields)
        # and they are organized by fieldset
        for fset in form.form_fieldsets():
            fset_node = node.xpath('//fieldset[@id="%s"]' % fset['id'])[0]
            if fset.get('title'):
                legend_node = fset_node.find('legend')
                self.assertEqual(legend_node.text, fset['title'])
            if fset.get('description'):
                desc_node = \
                    fset_node.find('p[@class="fieldset-description"]')
                self.assertEqual(desc_node.text, fset['description'])
            if fset.get('css_extra_klass'):
                self.assertEqual(
                    fset_node.attrib['class'], fset['css_extra_klass'])
            # check all fields are contained into it
            self.assert_match_inputs(fset_node, fset['fields'])

    def test_render_form_fieldsets_protected_field(self):
        """No field, no fieldset."""
        user = self.env.ref('base.user_demo')
        form = self.get_form('cms.form.test_fieldsets', sudo_uid=user.id)
        html = form.form_render()
        node = self.to_xml_node(html)[0]
        # we still get all the fields
        expected_fields = (
            'csrf_token',
            'a_char',
            'a_float',
            'a_number',
            'a_many2one',
            'a_many2many',
            'a_one2many',
        )
        # all fields are rendered
        self.assertEqual(
            len(node[0].xpath('//input|//select')), len(expected_fields)
        )
        self.assert_match_inputs(node, expected_fields)
        # protected field is not there
        self.assertFalse(node[0].xpath('//input[@name="ihaveagroup"]'))
        # also, since the field was the only one in the fieldset
        # the fieldset as well should be gone
        self.assertFalse(node[0].xpath('//fieldset[@id="protected"]'))
