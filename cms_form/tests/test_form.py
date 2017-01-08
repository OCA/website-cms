# -*- coding: utf-8 -*-
# Copyright 2016 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
# from openerp.tests import HttpCase
from openerp import http
from werkzeug.wrappers import Request
import mock
from cStringIO import StringIO
import urllib


def fake_request(form_data=None, query_string=None,
                 method='GET', content_type=None):
    data = urllib.urlencode(form_data or {})
    query_string = query_string or ''
    content_type = content_type or 'application/x-www-form-urlencoded'
    req = Request.from_values(
        query_string=query_string,
        content_length=len(data),
        input_stream=StringIO(data),
        content_type=content_type,
        method=method)
    req.session = mock.MagicMock()
    o_req = http.HttpRequest(req)
    o_req.website = mock.MagicMock()
    o_req.csrf_token = mock.MagicMock()
    return o_req


class TestForm(TransactionCase):

    at_install = False
    post_install = True

    def setUp(self):
        super(TestForm, self).setUp()

    def test_form_init(self):
        request = fake_request()
        form = self.env['cms.form'].new()
        form.form_init(request)
        self.assertTrue(isinstance(form.request, Request))
        self.assertTrue(isinstance(form.o_request, http.HttpRequest))

    def test_form_init_overrides(self):
        request = fake_request()
        form = self.env['cms.form'].new()
        form.form_init(request,
                       fields_whitelist=('name', ),
                       fields_blacklist=('country_id', ),
                       fields_attributes=('string', 'type', ))
        self.assertEqual(form._form_fields_whitelist, ('name', ))
        self.assertEqual(form._form_fields_blacklist, ('country_id', ))
        self.assertEqual(form._form_fields_attributes, ('string', 'type', ))

    def test_fields(self):
        form = self.env['cms.form.test_partner'].new()
        fields = form.form_fields()
        self.assertEqual(len(fields), 3)
        self.assertTrue('name' in fields.keys())
        self.assertTrue('country_id' in fields.keys())
        self.assertTrue('custom' in fields.keys())

        # whitelist
        form = self.env['cms.form.test_partner'].new()
        form.form_init(fake_request(), fields_whitelist=('name', ))
        fields = form.form_fields()
        self.assertEqual(len(fields), 1)
        self.assertTrue('name' in fields.keys())
        self.assertTrue('country_id' not in fields.keys())
        self.assertTrue('custom' not in fields.keys())

        # blacklist
        form = self.env['cms.form.test_partner'].new()
        form.form_init(fake_request(), fields_blacklist=('country_id', ))
        fields = form.form_fields()
        self.assertEqual(len(fields), 2)
        self.assertTrue('name' in fields.keys())
        self.assertTrue('country_id' not in fields.keys())
        self.assertTrue('custom' in fields.keys())

    def test_fields_order(self):
        form = self.env['cms.form.test_partner'].new()
        form.form_init(fake_request(),
                       fields_order=['name', 'custom', 'country_id', ])
        fields = form.form_fields()
        self.assertEqual(fields.keys()[0], 'name')
        self.assertEqual(fields.keys()[1], 'custom')
        self.assertEqual(fields.keys()[2], 'country_id')

        # change order
        form.form_init(fake_request(),
                       fields_order=['country_id', 'name', 'custom'])
        fields = form.form_fields()
        self.assertEqual(fields.keys()[0], 'country_id')
        self.assertEqual(fields.keys()[1], 'name')
        self.assertEqual(fields.keys()[2], 'custom')

    def test_fields_attributes(self):
        form = self.env['cms.form.test_partner'].new()
        fields = form.form_fields()
        # fields from partner model
        self.assertTrue(fields['name']['required'])
        self.assertTrue(fields['country_id']['required'])

    def test_load_defaults(self):
        form = self.env['cms.form.test_partner'].new()
        request = fake_request()
        form.form_init(request)

        # create mode, no main_object
        main_object = None
        defaults = form.form_load_defaults(main_object)
        expected = {
            'name': None,
            'country_id': None,
            'custom': 'oh yeah!'
        }
        for k, v in expected.iteritems():
            self.assertEqual(defaults[k], v)

        # write mode, have main_object
        main_object = self.env['res.partner'].new({})
        main_object.name = 'John Wayne'
        main_object.country_id = 5
        defaults = form.form_load_defaults(main_object)
        expected = {
            'name': 'John Wayne',
            'country_id': 5,
            'custom': 'oh yeah!'
        }
        for k, v in expected.iteritems():
            self.assertEqual(defaults[k], v)

        # values from request
        data = {
            'name': 'Paul Newman',
            'country_id': 7,
            'custom': 'yay!'
        }
        request = fake_request(form_data=data)
        form.form_init(request)
        defaults = form.form_load_defaults(main_object)
        for k, v in data.iteritems():
            self.assertEqual(defaults[k], v)

    def test_extract_from_request(self):
        form = self.env['cms.form.test_fields'].new()
        # values from request
        data = {
            'a_char': 'Jack White',
            'a_number': '10',
            'a_float': '5',
            'a_many2one': '123',
            'a_many2many': '1,2,3',
            'a_one2many': '4,5,6',
        }
        request = fake_request(form_data=data)
        form.form_init(request)
        values = form.form_extract_values()
        expected = {
            'a_char': 'Jack White',
            'a_number': 10,
            'a_float': 5.0,
            'a_many2one': 123,
            'a_many2many': [(6, False, [1, 2, 3]), ],
            'a_one2many': [(6, False, [4, 5, 6]), ],
        }
        for k, v in values.iteritems():
            self.assertEqual(expected[k], v)

    def test_validate(self):
        form = self.env['cms.form.test_fields'].new()
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
        form.form_init(request, required_fields=required)
        errors, errors_message = form.form_validate()
        self.assertTrue('a_char' in errors)
        self.assertTrue('a_float' in errors)
        self.assertTrue('a_many2one' in errors)
        self.assertTrue('a_many2many' in errors)

    def test_create_or_update(self):
        form = self.env['cms.form.test_partner'].new()
        # create
        data = {
            'name': 'Edward Norton',
        }
        request = fake_request(form_data=data, method='POST')
        form.form_init(request, required_fields=('name', ))
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
        form.form_init(
            request, main_object=main_object, required_fields=('name', ))
        main_object = form.form_create_or_update()
        self.assertEqual(main_object.name, data['name'])
        self.assertEqual(main_object.country_id.id, data['country_id'])

    def test_render(self):
        form = self.env['cms.form.test_fields'].new()
        request = fake_request()
        form.form_init(request)
        html = form.form_render()
        # TODO: test with html parsing
        self.assertTrue('<form' in html)
