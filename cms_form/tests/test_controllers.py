# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from contextlib import contextmanager
import mock
import os
import unittest

from .common import FormHttpTestCase
from ..controllers import main
from .fake_models import FakePartnerForm, FakeSearchPartnerForm, WIZ_KLASSES
from .utils import fake_request


IMPORT = 'odoo.addons.cms_form.controllers.main'


@unittest.skipIf(os.getenv('SKIP_HTTP_CASE'), 'HTTP case disabled.')
class TestControllers(FormHttpTestCase):

    TEST_MODELS_KLASSES = [
        FakePartnerForm, FakeSearchPartnerForm,
    ] + WIZ_KLASSES

    def setUp(self):
        super().setUp()
        self.form_controller = main.CMSFormController()
        self.form_search_controller = main.CMSSearchFormController()
        self.form_wiz_controller = main.CMSWizardFormController()
        self.authenticate('admin', 'admin')

    @contextmanager
    def mock_assets(self, req=None):
        """Mocks some stuff like request."""
        with mock.patch('%s.request' % IMPORT) as request:
            faked = req or fake_request()
            request.session = self.session
            request.env = self.env
            request.httprequest = faked.httprequest
            yield {
                'request': request,
            }

    def test_get_template(self):
        with self.mock_assets():
            form = self.form_controller.get_form('res.partner')
            # default
            self.assertEqual(
                self.form_controller.get_template(form),
                'cms_form.form_wrapper'
            )
            # custom on form
            form.form_wrapper_template = 'foo.baz'
            self.assertEqual(
                self.form_controller.get_template(form),
                'foo.baz'
            )
            self.form_controller.template = None
            form.form_wrapper_template = None
            with self.assertRaises(NotImplementedError):
                self.form_controller.get_template(form)

    def test_get_render_values(self):
        with self.mock_assets():
            form = self.form_controller.get_form('res.partner')
            # default, no main object
            self.assertEqual(
                self.form_controller.get_render_values(form),
                {
                    'form': form,
                    'main_object': self.env['res.partner'],
                    'controller': self.form_controller,
                }
            )
            # get a main obj
            partner = self.env.ref('base.res_partner_12')
            form = self.form_controller.get_form(
                'res.partner', model_id=partner.id)
            self.assertEqual(
                self.form_controller.get_render_values(form),
                {
                    'form': form,
                    'main_object': partner,
                    'controller': self.form_controller,
                }
            )
            # strip out form fields values (they are held by the form itself)
            self.assertEqual(
                self.form_controller.get_render_values(
                    form, name='John', custom='foo', not_a_form_field=1),
                {
                    'form': form,
                    'main_object': partner,
                    'controller': self.form_controller,
                    'not_a_form_field': 1
                }
            )

    def test_get_no_form(self):
        with self.mock_assets():
            # we do not have a specific form for res.groups
            # and cms form is not enabled on partner model
            with self.assertRaises(NotImplementedError):
                self.form_controller.get_form('res.groups')

    def test_get_form_no_model_no_main_object(self):
        with self.mock_assets():
            form = self.form_controller.get_form(
                None, form_model_key=FakePartnerForm._name)
            self.assertEqual(
                form.main_object, self.env[FakePartnerForm._name]
            )

    def test_get_default_form(self):
        with self.mock_assets():
            # we have one for res.partner
            form = self.form_controller.get_form('res.partner')
            self.assertTrue(
                isinstance(form, self.env['cms.form.res.partner'].__class__)
            )
            self.assertEqual(form._form_model, 'res.partner')
            self.assertEqual(form.form_mode, 'create')

    def test_get_specific_form(self):
        with self.mock_assets():
            # we have a specific form here
            form = self.form_search_controller.get_form('res.partner')
            self.assertTrue(
                isinstance(form,
                           self.env['cms.form.search.res.partner'].__class__)
            )
            self.assertEqual(form._form_model, 'res.partner')
            self.assertEqual(form.form_mode, 'search')

    def test_get_wizard_form(self):
        with self.mock_assets():
            # we have a specific form here
            form = self.form_wiz_controller.get_form('res.partner')
            self.assertTrue(
                isinstance(form,
                           self.env['cms.form.res.partner'].__class__)
            )
            self.assertEqual(form._form_model, 'res.partner')
            self.assertEqual(form.form_mode, 'create')

    def test_redirect_after_success(self):
        req = fake_request(
            form_data={'name': 'John'},
            method='POST',
        )
        with self.mock_assets(req=req):
            partner = self.env.ref('base.res_partner_12')
            response = self.form_controller.make_response(
                'res.partner', model_id=partner.id)
            self.assertEqual(response.status_code, 303)
            if 'website_url' in partner:
                # website_partner installed
                self.assertEqual(response.location, partner.website_url)
            else:
                self.assertEqual(response.location, '/')

    def _check_rendering(self, dom, form_model, model, mode, extra_klass=''):
        """Check default markup for form and form wrapper."""
        # test wrapper klass
        wrapper_node = dom.find_class('cms_form_wrapper')[0]
        expected_attrs = {
            'class':
                'cms_form_wrapper {form_model} {model} mode_{mode}'.format(
                    form_model=form_model.replace('.', '_'),
                    model=model.replace('.', '_'),
                    mode=mode
                ) + (' ' + extra_klass if extra_klass else '')
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

    def _check_route(self, url):
        resp = self.url_open(url, timeout=30)
        self.assertTrue(resp.ok)
        self.assertEqual(resp.status_code, 200)

    def test_default_routes(self):
        self._check_route('/cms/create/res.partner')
        self._check_route('/cms/edit/res.partner/1')
        self._check_route('/cms/search/res.partner')
        self._check_route('/cms/ajax/search/res.partner')

    def test_default_create_rendering(self):
        dom = self.html_get('/cms/create/res.partner')
        self._check_rendering(
            dom, 'cms.form.res.partner', 'res.partner', 'create')

    def test_default_edit_rendering(self):
        partner = self.env.ref('base.res_partner_1')
        dom = self.html_get('/cms/edit/res.partner/{}'.format(partner.id))
        self._check_rendering(
            dom, 'cms.form.res.partner', 'res.partner', 'edit')

    def _check_wiz_rendering(
            self, dom, form_model, model, mode, extra_klass=''):
        self._check_rendering(
            dom, form_model, model, mode, extra_klass=extra_klass)
        # TODO: check more (paging etc)

    def test_default_wiz_rendering(self):
        dom = self.html_get('/cms/wiz/fake.wiz/page/1')
        self._check_wiz_rendering(
            dom, 'fake.wiz.step1.country',
            'res.country', 'wizard', extra_klass='fake_wiz')
        dom = self.html_get('/cms/wiz/fake.wiz/page/2')
        self._check_wiz_rendering(
            dom, 'fake.wiz.step2.partner',
            'res.partner', 'wizard', extra_klass='fake_wiz')
        dom = self.html_get('/cms/wiz/fake.wiz/page/3')
        self._check_wiz_rendering(
            dom, 'fake.wiz.step3.partner',
            'res.partner', 'wizard', extra_klass='fake_wiz')
