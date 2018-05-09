# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from contextlib import contextmanager
import mock

from .common import FormHttpTestCase
from ..controllers import main
from .fake_models import FakePartnerForm, FakeSearchPartnerForm
from .utils import fake_request


IMPORT = 'odoo.addons.cms_form.controllers.main'


class TestControllers(FormHttpTestCase):

    TEST_MODELS_KLASSES = [FakePartnerForm, FakeSearchPartnerForm]

    def setUp(self):
        super(TestControllers, self).setUp()
        self.form_controller = main.CMSFormController()
        self.form_search_controller = main.CMSSearchFormController()
        self.authenticate('admin', 'admin')

    @contextmanager
    def mock_assets(self):
        """Mocks some stuff like request."""
        with mock.patch('%s.request' % IMPORT) as request:
            faked = fake_request()
            request.session = self.session
            request.env = self.env
            request.httprequest = faked.httprequest
            yield {
                'request': request,
            }

    def test_get_form(self):
        with self.mock_assets():
            # we do not have a specific form for res.groups
            # and cms form is not enabled on partner model
            with self.assertRaises(NotImplementedError):
                form = self.form_controller.get_form('res.groups')

            # but we have one for res.partner
            form = self.form_controller.get_form('res.partner')
            self.assertTrue(
                isinstance(form, self.env['cms.form.res.partner'].__class__)
            )
            self.assertEqual(form._form_model, 'res.partner')
            self.assertEqual(form.form_mode, 'create')
            self.assertTrue(form)

            # we have a specific form here
            form = self.form_search_controller.get_form('res.partner')
            self.assertTrue(
                isinstance(form,
                           self.env['cms.form.search.res.partner'].__class__)
            )
            self.assertEqual(form._form_model, 'res.partner')
            self.assertEqual(form.form_mode, 'search')

    def _check_route(self, url, model, mode):
        """Check default markup for form and form wrapper."""
        # with self.mock_assets():
        dom = self.html_get(url)
        # test wrapper klass
        wrapper_node = dom.find_class('cms_form_wrapper')[0]
        expected_attrs = {
            'class':
                'cms_form_wrapper {form_model} {model} mode_{mode}'.format(
                    form_model='cms_form_res_partner',
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
