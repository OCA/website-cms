# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import mock
from odoo.tools import mute_logger

from .common import FormTestCase
from .utils import fake_request
from .fake_models import FakePartnerForm, FakeFieldsForm


class TestCMSForm(FormTestCase):

    TEST_MODELS_KLASSES = [FakePartnerForm, FakeFieldsForm]

    @classmethod
    def setUpClass(cls):
        super(TestCMSForm, cls).setUpClass()
        cls._setup_models()

    @classmethod
    def tearDownClass(cls):
        cls._teardown_models()
        super(TestCMSForm, cls).tearDownClass()

    def test_validate(self):
        form = self.get_form('cms.form.test_fields')
        # values from request
        data = {
            'a_char': 'Foo',
            'a_number': '10',
            'a_float': '5',
            'a_many2one': '',
            'a_many2many': '',
        }
        request = fake_request(form_data=data)
        required = (
            'a_many2one', 'a_many2many'
        )
        form = self.get_form(
            'cms.form.test_fields', req=request, required_fields=required)
        errors, errors_message = form.form_validate()
        self.assertTrue('a_char' in errors)
        self.assertTrue('a_float' in errors)
        self.assertTrue('a_many2one' in errors)
        self.assertTrue('a_many2many' in errors)

    def test_create_or_update(self):
        # create
        data = {
            'name': 'Edward Norton',
        }
        request = fake_request(form_data=data, method='POST')
        form = self.get_form(
            'cms.form.res.partner',
            req=request,
            required_fields=('name', ))
        main_object = form.form_create_or_update()
        self.assertEqual(main_object._name, 'res.partner')
        self.assertEqual(main_object.name, data['name'])
        # update
        data = {
            'name': 'Edward Flip',
            'country_id': 1,
            'custom': 'foo',
        }
        request = fake_request(form_data=data, method='POST')
        form = self.get_form(
            'cms.form.res.partner',
            req=request,
            required_fields=('name', ))
        main_object = form.form_create_or_update()
        self.assertEqual(main_object.name, data['name'])
        self.assertEqual(main_object.country_id.id, data['country_id'])

    def test_create_or_update_with_errors(self):
        request = fake_request(form_data={}, method='POST')
        form = self.get_form(
            'cms.form.res.partner',
            req=request)
        with mute_logger('odoo.sql_db'):
            values = form.form_process_POST({})
        self.assertTrue(
            # custom modules can provide different errors for constraints
            '_integrity' in values['errors'] or
            '_validation' in values['errors']
        )

    def test_purge_non_model_fields(self):
        data = {
            'name': 'Johnny Glamour',
            'custom': 'Remove me from write and create, tnx!'
        }
        request = fake_request(form_data=data, method='POST')
        form = self.get_form(
            'cms.form.res.partner',
            req=request)
        to_patch = \
            'odoo.addons.cms_form.models.cms_form.CMSForm._form_create'
        with mock.patch(to_patch) as patched:
            form.form_create_or_update()
            patched.assert_called_with({'name': 'Johnny Glamour'})

        main_object = self.env['res.partner'].create({'name': 'Update Me'})
        request = fake_request(form_data=data, method='POST')
        form = self.get_form(
            'cms.form.res.partner',
            main_object=main_object,
            req=request)
        to_patch = \
            'odoo.addons.cms_form.models.cms_form.CMSForm._form_write'
        with mock.patch(to_patch) as patched:
            form.form_create_or_update()
            patched.assert_called_with({'name': 'Johnny Glamour'})
