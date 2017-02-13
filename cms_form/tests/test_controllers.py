# -*- coding: utf-8 -*-
# Copyright 2016 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# from .common import fake_request
from .common import FormHttpTestCase
from ..controllers import main
import mock
from contextlib import contextmanager

IMPORT = 'openerp.addons.cms_form.controllers.main'


class TestControllers(FormHttpTestCase):

    def setUp(self):
        super(TestControllers, self).setUp()
        self.form_controller = main.CMSFormController()
        self.form_search_controller = main.CMSSearchFormController()
        self.authenticate('admin', 'admin')

    @contextmanager
    def mock_assets(self):
        """Mocks some stuff like request."""
        with mock.patch('%s.request' % IMPORT) as request:
            request.session = self.session
            request.env = self.env
            yield {
                'request': request,
            }

    def test_get_form(self):
        with self.mock_assets():
            form = self.form_controller.get_form('res.partner')
            self.assertTrue(form)
            self.assertEqual(form._form_model, 'res.partner')

    def _check_route(self, url, model, mode):
        """Check default markup for form and form wrapper."""
        dom = self.html_get(url)
        # test wrapper klass
        wrapper_node = dom.find_class('cms_form_wrapper')[0]
        expected_attrs = {
            'class':
                'cms_form_wrapper {model} mode_{mode}'.format(
                    model=model.replace('.', '_'),
                    mode=mode
                )
        }
        self.assert_match_attrs(wrapper_node.attrib, expected_attrs)
        # test form is there and has correct klass
        form_node = dom.xpath('//form')[0]
        expected_attrs = {
            'enctype': 'multipart/form-data',
            'method': 'POST',
            'class': 'form-horizontal'
        }
        self.assert_match_attrs(form_node.attrib, expected_attrs)

    def test_default_routes(self):
        self._check_route(
            '/cms/form/create/res.partner',
            'res.partner',
            'create')
        partner = self.env.ref('base.res_partner_1')
        self._check_route(
            '/cms/form/edit/res.partner/{}'.format(partner.id),
            'res.partner',
            'edit')
