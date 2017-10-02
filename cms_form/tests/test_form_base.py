# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from werkzeug.wrappers import Request

from odoo import http

from .common import fake_request, FormTestCase


class TestFormBase(FormTestCase):

    def test_form_init(self):
        form = self.get_form('cms.form.mixin')
        self.assertTrue(isinstance(form.request, Request))
        self.assertTrue(isinstance(form.o_request, http.HttpRequest))

    def test_form_init_overrides(self):
        overrides = dict(
            model='res.partner',
            mode='foo',
            fields_whitelist=('name', ),
            fields_blacklist=('country_id', ),
            fields_attributes=('string', 'type', ),
            wrapper_extra_css_klass='foo',
            extra_css_klass='baz',
        )
        form = self.get_form('cms.form.mixin', **overrides)
        for k, v in overrides.iteritems():
            self.assertEqual(getattr(form, '_form_' + k), v)

    def test_fields_load(self):
        form = self.get_form('cms.form.res.partner')
        fields = form.form_fields()
        self.assertEqual(len(fields), 3)
        self.assertTrue('name' in fields.keys())
        self.assertTrue('country_id' in fields.keys())
        self.assertTrue('custom' in fields.keys())

        # whitelist
        form = self.get_form(
            'cms.form.res.partner',
            fields_whitelist=('name', ))
        fields = form.form_fields()
        self.assertEqual(len(fields), 1)
        self.assertTrue('name' in fields.keys())
        self.assertTrue('country_id' not in fields.keys())
        self.assertTrue('custom' not in fields.keys())

        # blacklist
        form = self.get_form(
            'cms.form.res.partner',
            fields_blacklist=('country_id', ))
        fields = form.form_fields()
        self.assertEqual(len(fields), 2)
        self.assertTrue('name' in fields.keys())
        self.assertTrue('country_id' not in fields.keys())
        self.assertTrue('custom' in fields.keys())

    def test_fields_order(self):
        form = self.get_form(
            'cms.form.res.partner',
            fields_order=['name', 'custom', 'country_id', ])
        fields = form.form_fields()
        self.assertEqual(fields.keys()[0], 'name')
        self.assertEqual(fields.keys()[1], 'custom')
        self.assertEqual(fields.keys()[2], 'country_id')

        # change order
        form = self.get_form(
            'cms.form.res.partner',
            fields_order=['country_id', 'name', 'custom'])
        fields = form.form_fields()
        self.assertEqual(fields.keys()[0], 'country_id')
        self.assertEqual(fields.keys()[1], 'name')
        self.assertEqual(fields.keys()[2], 'custom')

    def test_fields_attributes(self):
        form = self.get_form('cms.form.res.partner')
        fields = form.form_fields()
        # this one is required in partner model
        self.assertTrue(fields['name']['required'])
        # this one is forced to required in our custom form
        self.assertTrue(fields['country_id']['required'])

    def test_get_loader(self):
        form = self.get_form('cms.form.test_fields')
        expected = {}.fromkeys((
            'a_char',
            'a_number',
            'a_float',
            'a_many2one',
            'a_one2many',
            'a_many2many',
        ), None)
        fields = form.form_fields()
        for fname, loader in expected.iteritems():
            self.assertEqual(
                loader, form.form_get_loader(fname, fields[fname])
            )

        def custom_loader(*pa, **ka):
            return pa, ka

        # by type
        form._form_load_char = custom_loader
        form._form_load_integer = custom_loader
        form._form_load_float = custom_loader
        # by name
        form._form_load_a_many2many = custom_loader

        for fname in ('a_char', 'a_number', 'a_float', 'a_many2many'):
            self.assertEqual(
                custom_loader,
                form.form_get_loader(fname, fields[fname])
            )

    def test_get_extractor(self):
        form = self.get_form('cms.form.test_fields')
        expected = {}.fromkeys((
            'a_char',
            'a_number',
            'a_float',
            'a_many2one',
            'a_one2many',
            'a_many2many',
        ), None)
        fields = form.form_fields()
        for fname, loader in expected.iteritems():
            self.assertEqual(
                loader, form.form_get_extractor(fname, fields[fname])
            )

        def custom_extractor(*pa, **ka):
            return pa, ka

        # by type
        form._form_extract_char = custom_extractor
        form._form_extract_integer = custom_extractor
        form._form_extract_float = custom_extractor
        # by name
        form._form_extract_a_many2many = custom_extractor

        for fname in ('a_char', 'a_number', 'a_float', 'a_many2many'):
            self.assertEqual(
                custom_extractor,
                form.form_get_extractor(fname, fields[fname])
            )

    def test_load_defaults(self):
        # create mode, no main_object
        main_object = None
        form = self.get_form('cms.form.res.partner', main_object=main_object)
        defaults = form.form_load_defaults()
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
        form = self.get_form('cms.form.res.partner', main_object=main_object)
        defaults = form.form_load_defaults()
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
        form = self.get_form(
            'cms.form.res.partner', req=request, main_object=main_object)
        defaults = form.form_load_defaults()
        for k, v in data.iteritems():
            self.assertEqual(defaults[k], v)

    def test_extract_from_request(self):
        form = self.get_form('cms.form.test_fields')
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
        # write mode
        form = self.get_form('cms.form.test_fields', req=request)
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
        # read mode
        form = self.get_form(
            'cms.form.test_fields', req=request, extract_value_mode='read')
        values = form.form_extract_values()
        expected.update({
            'a_many2many': [1, 2, 3],
            'a_one2many': [4, 5, 6],
        })
        for k, v in values.iteritems():
            self.assertEqual(expected[k], v)
