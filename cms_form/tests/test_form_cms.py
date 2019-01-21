# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import mock
from odoo import exceptions
from odoo.tools import mute_logger

from .common import FormTestCase
from .utils import fake_request
from .fake_models import (
    FakePartnerForm,
    FakeFieldsForm,
    FakePartnerChannelForm,
    FakePubModel,
    FakePubModelForm,
)


class TestCMSForm(FormTestCase):

    TEST_MODELS_KLASSES = [
        FakePartnerForm,
        FakeFieldsForm,
        FakePartnerChannelForm,
        FakePubModel,
        FakePubModelForm,
    ]

    @classmethod
    def setUpClass(cls):
        super(TestCMSForm, cls).setUpClass()
        cls._setup_models()

    @classmethod
    def tearDownClass(cls):
        cls._teardown_models()
        super(TestCMSForm, cls).tearDownClass()

    def test_form_base_attrs(self):
        form = self.get_form('cms.form.test_fields')
        # no form model, no default title
        self.assertEqual(form.form_title, '')
        form = self.get_form('cms.form.res.partner')
        # form model present, title now depends on mode and model descr
        # no record to edit, create mode on
        self.assertEqual(form.form_mode, 'create')
        self.assertEqual(form.form_title, 'Create Contact')
        # now edit a record
        partner = self.env.ref('base.main_partner')
        form = self.get_form('cms.form.res.partner', main_object=partner)
        self.assertEqual(form.form_mode, 'edit')
        self.assertEqual(form.form_title, 'Edit "%s"' % partner.name)
        # now edit a record that has a m2o as rec name
        partner.name = 'Johnny'
        partner_channel = self.env['mail.channel.partner'].create({
            'partner_id': partner.id,
        })
        form = self.get_form(
            'cms.form.mail.channel.partner',
            main_object=partner_channel
        )
        self.assertEqual(form.form_title, 'Edit "Johnny"')

    def test_form_special_attrs_getter_setter(self):
        form = self.get_form('cms.form.test_fields')
        # submit success flag
        self.assertFalse(form.form_success)
        form.form_success = True
        self.assertTrue(form.form_success)
        # submit redirect flag
        self.assertFalse(form.form_redirect)
        form.form_redirect = True
        self.assertTrue(form.form_redirect)

    def test_next_url(self):
        # no record, no redirrect param, default to root
        form = self.get_form('cms.form.res.partner')
        self.assertEqual(form.form_next_url(), '/')
        # redirect param in request
        request = fake_request(query_string='redirect=/foo')
        form = self.get_form(
            'cms.form.res.partner',
            req=request)
        self.assertEqual(form.form_next_url(), '/foo')
        # edit a record: get to its ws URL
        record = self.env['fake.publishable'].create({'name': 'Baz'})
        form = self.get_form(
            'cms.form.fake.publishable',
            main_object=record
        )
        self.assertEqual(form.form_next_url(), '/publishable/%d' % record.id)
        # edit a record that has an URL but got redirect in request
        request = fake_request(query_string='redirect=/sorry/go/here')
        form = self.get_form(
            'cms.form.fake.publishable',
            req=request,
            main_object=record,
        )
        self.assertEqual(form.form_next_url(), '/sorry/go/here')

    def test_cancel_url(self):
        # no record, no redirrect param, default to root
        form = self.get_form('cms.form.res.partner')
        self.assertEqual(form.form_cancel_url(), '/')
        # redirect param in request
        request = fake_request(query_string='redirect=/foo')
        form = self.get_form(
            'cms.form.res.partner',
            req=request)
        self.assertEqual(form.form_cancel_url(), '/foo')
        # edit a record: get to its ws URL
        record = self.env['fake.publishable'].create({'name': 'Baz'})
        form = self.get_form(
            'cms.form.fake.publishable',
            main_object=record
        )
        self.assertEqual(form.form_cancel_url(), '/publishable/%d' % record.id)
        # edit a record that has an URL but got redirect in request
        request = fake_request(query_string='redirect=/sorry/go/here')
        form = self.get_form(
            'cms.form.fake.publishable',
            req=request,
            main_object=record,
        )
        self.assertEqual(form.form_cancel_url(), '/sorry/go/here')

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
        self.assertEqual(errors, {
            'a_char': True,
            'a_float': True,
            'a_many2many': 'missing',
            'a_many2one': 'missing',
        })
        self.assertEqual(errors_message, {
            'a_char': 'Text length must be greater than 8!',
            'a_float': 'Must be greater than 5!',
        })

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
        form.form_process()
        main_object = form.main_object
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
            main_object=main_object,
            required_fields=('name', ))
        form.form_process()
        self.assertEqual(main_object.name, data['name'])
        self.assertEqual(main_object.country_id.id, data['country_id'])

    def test_create_or_update_with_errors(self):
        request = fake_request(form_data={}, method='POST')
        form = self.get_form(
            'cms.form.res.partner',
            req=request)
        with mute_logger('odoo.sql_db'):
            values = form.form_process_POST({})
        self.assertFalse(form.form_success)
        self.assertTrue(
            # custom modules can provide different errors for constraints
            '_integrity' in values['errors'] \
            or '_validation' in values['errors']
        )
        with mock.patch.object(type(form), 'form_create_or_update') as mocked:
            random_msg = (
                'Error while validating constraint\n'
                '\nEnd Date cannot be set before Start Date.\nNone'
            )
            mocked.side_effect = exceptions.ValidationError(random_msg)
            values = form.form_process_POST({})
            # validation error flag
            self.assertEqual(values['errors'], {'_validation': True})
            # formatted error message
            self.assertEqual(
                values['errors_message'], {
                    '_validation': 'Error while validating constraint'
                                   '<br />'
                                   'End Date cannot be set before Start Date.'
                }
            )

    def test_purge_non_model_fields_no_model(self):
        form = self.get_form('cms.form.test_fields')
        self.assertEqual(form._form_purge_non_model_fields({}), {})

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
