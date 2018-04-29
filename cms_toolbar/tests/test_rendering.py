# Copyright 2018 Camptocamp - Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.cms_form.tests.common import FormRenderTestCase
from .fake_models import FakePublishModel


class HTMLCase(FormRenderTestCase):

    TEST_MODELS_KLASSES = [FakePublishModel, ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_models()
        cls.record = cls.env[FakePublishModel._name].create({'name': 'Foo'})

    @classmethod
    def tearDownClass(cls):
        cls._teardown_models()
        super().tearDownClass()

    xpr = (
        "(//a[contains(@class, '{klass}')] |"
        " //button[contains(@class, '{klass}')])"
    )

    def test_render_wrapper(self):
        html = self.record.cms_render_toolbar()
        node = self.to_xml_node(html)[0]
        wrapper = node.find_class('cms_toolbar')[0]
        self.assertEqual(
            wrapper.attrib['class'], 'cms_toolbar fake_publishable')

    def _test_render(self, html, expected, not_expected=None, popover=True):
        node = self.to_xml_node(html)[0]
        for klass in expected:
            el = node.xpath(self.xpr.format(klass=klass))
            self.assertTrue(el)
        for klass in not_expected or []:
            el = node.xpath(self.xpr.format(klass=klass))
            self.assertFalse(el)
        popover_el = node.xpath('//div[@id="popover_html_content"]')
        if popover:
            self.assertTrue(popover_el)
        else:
            self.assertFalse(popover_el)

    def test_render1(self):
        html = self.record.cms_render_toolbar()
        expected = ('edit', 'create', 'publish', 'delete')
        self._test_render(html, expected)

    def test_render2(self):
        html = self.record.cms_render_toolbar(show_edit=False)
        expected = ('create', 'publish', 'delete')
        not_expected = ('edit', )
        self._test_render(html, expected, not_expected=not_expected)

    def test_render3(self):
        html = self.record.cms_render_toolbar(
            show_edit=False, show_create=False)
        expected = ('publish', 'delete')
        not_expected = ('create', 'edit', )
        self._test_render(html, expected, not_expected=not_expected)

    def test_render4(self):
        html = self.record.cms_render_toolbar(
            show_edit=False, show_create=False, show_delete=False)
        expected = ('publish', )
        not_expected = ('create', 'edit', 'delete')
        self._test_render(html, expected, not_expected=not_expected)

    def test_render5(self):
        html = self.record.cms_render_toolbar(
            show_edit=False, show_create=False,
            show_delete=False, show_publish=False)
        # nothing is rendered, toolbar wrapper neither
        self.assertFalse(html.strip())

    def test_render6(self):
        html = self.record.cms_render_toolbar(show_popover=False)
        expected = ('edit', 'create', 'publish', 'delete')
        self._test_render(html, expected, popover=False)
