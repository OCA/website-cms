# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import mock
from werkzeug.wrappers import Request

from odoo import http

from .common import FormTestCase
from .utils import fake_request
from .fake_models import (
    FakePartnerForm,
    FakeFieldsForm,
    FakePartnerFormProtectedFields,
)


class TestFormBase(FormTestCase):

    TEST_MODELS_KLASSES = [
        FakePartnerForm,
        FakeFieldsForm,
        FakePartnerFormProtectedFields,
    ]

    @classmethod
    def setUpClass(cls):
        super(TestFormBase, cls).setUpClass()
        cls._setup_models()

    @classmethod
    def tearDownClass(cls):
        cls._teardown_models()
        super(TestFormBase, cls).tearDownClass()

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
        for k, v in overrides.items():
            self.assertEqual(getattr(form, '_form_' + k), v)

    def test_form_mode(self):
        form = self.get_form('cms.form.mixin')
        self.assertEqual(form.form_mode, 'create')
        form = self.get_form('cms.form.mixin', main_object=object())
        self.assertEqual(form.form_mode, 'edit')
        form = self.get_form('cms.form.mixin', mode='custom')
        self.assertEqual(form.form_mode, 'custom')

    def test_fields_load(self):
        form = self.get_form('cms.form.res.partner')
        fields = form.form_fields()
        self.assertEqual(len(fields), 3)
        self.assertTrue('name' in list(fields.keys()))
        self.assertTrue('country_id' in list(fields.keys()))
        self.assertTrue('custom' in list(fields.keys()))

        # whitelist
        form = self.get_form(
            'cms.form.res.partner',
            fields_whitelist=('name', ))
        fields = form.form_fields()
        self.assertEqual(len(fields), 1)
        self.assertTrue('name' in list(fields.keys()))
        self.assertTrue('country_id' not in list(fields.keys()))
        self.assertTrue('custom' not in list(fields.keys()))

        # blacklist
        form = self.get_form(
            'cms.form.res.partner',
            fields_blacklist=('country_id', ))
        fields = form.form_fields()
        self.assertEqual(len(fields), 2)
        self.assertTrue('name' in list(fields.keys()))
        self.assertTrue('country_id' not in list(fields.keys()))
        self.assertTrue('custom' in list(fields.keys()))

    def test_fields_order(self):
        form = self.get_form(
            'cms.form.res.partner',
            fields_order=['name', 'custom', 'country_id', ])
        fields = form.form_fields()
        self.assertEqual(list(fields.keys())[0], 'name')
        self.assertEqual(list(fields.keys())[1], 'custom')
        self.assertEqual(list(fields.keys())[2], 'country_id')

        # change order
        form = self.get_form(
            'cms.form.res.partner',
            fields_order=['country_id', 'name', 'custom'])
        fields = form.form_fields()
        self.assertEqual(list(fields.keys())[0], 'country_id')
        self.assertEqual(list(fields.keys())[1], 'name')
        self.assertEqual(list(fields.keys())[2], 'custom')

    def test_fields_attributes(self):
        form = self.get_form('cms.form.res.partner')
        fields = form.form_fields()
        # this one is required in partner model
        self.assertTrue(fields['name']['required'])
        # this one is forced to required in our custom form
        self.assertTrue(fields['country_id']['required'])

    def test_fields_defaults(self):
        form = self.get_form('cms.form.res.partner')
        self.env['ir.default'].set('res.partner', 'name', 'DEFAULT NAME')
        fields = form.form_fields()
        self.assertEqual(fields['name']['_default'], 'DEFAULT NAME')
        self.assertEqual(fields['custom']['_default'], 'I am your default')

    def test_fields_hidden(self):
        form = self.get_form(
            'cms.form.res.partner', fields_hidden=('country_id', ))
        # get all fields (default)
        fields = form.form_fields()
        self.assertListEqual(
            sorted(fields.keys()), ['country_id', 'custom', 'name', ])
        # country is flagged as hidden
        self.assertTrue(fields['country_id']['hidden'])
        # get only visible
        fields = form.form_fields(hidden=False)
        self.assertListEqual(sorted(fields.keys()), ['custom', 'name'])
        # get only hidden
        fields = form.form_fields(hidden=True)
        self.assertListEqual(sorted(fields.keys()), ['country_id', ])
        self.assertTrue(fields['country_id']['hidden'])

    def test_fields_hidden_keep_order(self):
        form = self.get_form(
            'cms.form.res.partner',
            fields_hidden=('country_id', ),
            fields_order=['country_id', 'name', 'custom'])
        fields = form.form_fields(hidden=False)
        self.assertListEqual(
            list(fields.keys()), ['name', 'custom'])
        form = self.get_form(
            'cms.form.res.partner',
            fields_hidden=('country_id', ),
            fields_order=['country_id', 'custom', 'name'])
        fields = form.form_fields(hidden=False)
        self.assertListEqual(
            list(fields.keys()), ['custom', 'name', ])

    def test_subfields(self):
        form = self.get_form(
            'cms.form.res.partner',
            sub_fields={
                'name': {'_all': ('custom', )},
                'do_not_exists': {'_all': ('foo', )}  # skipped
            }
        )
        fields = form.form_fields()
        self.assertEqual(
            fields['name']['subfields'],
            {'_all': {'custom': fields['custom']}}
        )
        self.assertTrue(fields['custom']['is_subfield'])

    def test_fields_binary(self):
        form = self.get_form(
            'cms.form.res.partner',
            model_fields=['name', 'image']
        )
        self.assertEqual(list(form.form_file_fields.keys()), ['image', ])

    def test_fields_protected(self):
        group = self.env.ref('website.group_website_designer')
        user = self.env.ref('base.user_demo')
        # user does not have the group
        self.assertNotIn(group, user.groups_id)
        form = self.get_form('cms.form.protected.fields', sudo_uid=user.id)
        fields = form.form_fields()
        # field is skipped
        self.assertEqual(list(fields.keys()), ['nogroup'])
        # now add the group
        user.write({'groups_id': [(4, group.id)]})
        fields = form.form_fields()
        # now we get protected field too
        self.assertEqual(list(fields.keys()), ['ihaveagroup', 'nogroup', ])

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
        for fname, loader in expected.items():
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
        for fname, loader in expected.items():
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
        for k, v in expected.items():
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
        for k, v in expected.items():
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
        for k, v in data.items():
            self.assertEqual(defaults[k], v)

    # TODO: test marshallers integration
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
        for k, v in values.items():
            self.assertEqual(expected[k], v)
        # read mode
        form = self.get_form(
            'cms.form.test_fields', req=request, extract_value_mode='read')
        values = form.form_extract_values()
        expected.update({
            'a_many2many': [1, 2, 3],
            'a_one2many': [4, 5, 6],
        })
        for k, v in values.items():
            self.assertEqual(expected[k], v)

    def test_extract_from_request_no_value(self):
        """If you submit no value for a field it gets ignored."""
        form = self.get_form('cms.form.test_fields')
        # values from request
        data = {
            # not convertable value -> we'll get None
            'a_float': '5/0',
            'a_number': '10A',
        }
        request = fake_request(form_data=data)
        form = self.get_form('cms.form.test_fields', req=request)
        values = form.form_extract_values()
        # these are converted to `None` and ignored
        for fname in ['a_char', 'a_number', 'a_float', 'a_many2one', ]:
            self.assertNotIn(fname, values)
        # special case: when you don't submit a value form x2m we wipe it
        for fname in ['a_many2many', 'a_one2many', ]:
            self.assertEqual(values[fname], [(5, )])

    def test_extract_from_request_custom_extractor(self):
        # test custom extractor integration w/ form_extract_values
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

        def custom_extractor(form, fname, value, **request_values):
            return 'custom for: ' + fname

        # by type
        form._form_extract_a_char = custom_extractor
        form._form_extract_a_number = custom_extractor
        values = form.form_extract_values()
        expected = {
            'a_char': 'custom for: a_char',
            'a_number': 'custom for: a_number',
            'a_float': 5.0,
            'a_many2one': 123,
            'a_many2many': [(6, False, [1, 2, 3]), ],
            'a_one2many': [(6, False, [4, 5, 6]), ],
        }
        for k, v in values.items():
            self.assertEqual(expected[k], v)

    def test_form_process_GET(self):
        form = self.get_form('cms.form.test_fields')
        self.assertEqual(
            form.form_render_values, {
                'main_object': None,
                'form': form,
                'form_data': {},
                'errors': {},
                'errors_messages': {},
            }
        )
        with mock.patch.object(type(form), 'form_process_GET') as handler:
            handler.return_value = {
                'extra_key1': 'foo',
                'extra_key2': 'baz',
            }
            form.form_process()
            # the right process method has been called
            handler.assert_called()
            # and got called w/ the right render values
            default_form_data = {
                'a_char': None,
                'a_float': None,
                'a_many2many': '[]',
                'a_many2one': None,
                'a_number': None,
                'a_one2many': '[]'
            }
            expected = {
                'main_object': None,
                'form': form,
                'form_data': default_form_data,
                'errors': {},
                'errors_messages': {},
            }
            handler.assert_called_with(expected)
            # and the result of the handler is injected into render values
            self.assertEqual(form.form_render_values, {
                # extra args have been injected
                'extra_key1': 'foo',
                'extra_key2': 'baz',
                'main_object': None,
                'form': form,
                'form_data': default_form_data,
                'errors': {},
                'errors_messages': {},
            })

    def test_form_process_POST(self):
        request = fake_request(method='POST')
        form = self.get_form('cms.form.test_fields', req=request)
        with mock.patch.object(type(form), 'form_process_POST') as handler:
            handler.return_value = {
                'extra_key3': 'foo',
                'extra_key4': 'baz',
            }
            form.form_process()
            # the right process method has been called
            handler.assert_called()
            # and got called w/ the right render values
            default_form_data = {
                'a_char': None,
                'a_float': None,
                'a_many2many': '[]',
                'a_many2one': None,
                'a_number': None,
                'a_one2many': '[]'
            }
            expected = {
                'main_object': None,
                'form': form,
                'form_data': default_form_data,
                'errors': {},
                'errors_messages': {},
            }
            handler.assert_called_with(expected)
            # self.assert_nested_dict_equal(call_args, expected)
            # and the result of the handler is injected into render values
            self.assertEqual(form.form_render_values, {
                # extra args have been injected
                'extra_key3': 'foo',
                'extra_key4': 'baz',
                'main_object': None,
                'form': form,
                'form_data': default_form_data,
                'errors': {},
                'errors_messages': {},
            })

    def test_get_widget(self):
        form = self.get_form('cms.form.test_fields')
        expected = {
            'a_char': 'cms.form.widget.char',
            'a_number': 'cms.form.widget.integer',
            'a_float': 'cms.form.widget.float',
            'a_many2one': 'cms.form.widget.many2one',
            'a_many2many': 'cms.form.widget.many2many',
            'a_one2many': 'cms.form.widget.one2many',
        }
        fields = form.form_fields()
        for fname, widget_model in expected.items():
            self.assertEqual(
                widget_model, form.form_get_widget_model(fname, fields[fname])
            )
            self.assertEqual(
                form.form_get_widget(fname, fields[fname]).__class__,
                self.env[widget_model].__class__
            )

    def test_wrapper_css_klass(self):
        form = self.get_form('cms.form.res.partner')
        expected = (
            'cms_form_wrapper cms_form_res_partner '
            'res_partner mode_create'
        )
        self.assertEqual(
            form.form_wrapper_css_klass,
            expected
        )
        form._form_wrapper_extra_css_klass = 'foo'
        expected = (
            'cms_form_wrapper cms_form_res_partner '
            'res_partner foo mode_create'
        )
        self.assertEqual(
            form.form_wrapper_css_klass,
            expected
        )

    def test_css_klass(self):
        form = self.get_form('cms.form.res.partner')
        self.assertEqual(form.form_css_klass, 'form-horizontal')
        form._form_extra_css_klass = 'cool'
        self.assertEqual(form.form_css_klass, 'form-horizontal cool')
        form.form_display_mode = 'vertical'
        self.assertEqual(form.form_css_klass, 'form-vertical cool')

    def test_field_wrapper_css_klass(self):
        form = self.get_form('cms.form.res.partner')
        self.assertEqual(
            form.form_make_field_wrapper_klass(
                'foo_field', {
                    'type': 'char',
                    'required': False,
                }
            ), 'form-group form-field field-char field-foo_field'
        )
        self.assertEqual(
            form.form_make_field_wrapper_klass(
                'foo_field_id', {
                    'type': 'many2one',
                    'required': True,
                }
            ), ('form-group form-field field-many2one '
                'field-foo_field_id field-required')
        )
        self.assertEqual(
            form.form_make_field_wrapper_klass(
                'foo_field', {
                    'type': 'float',
                    'required': True,
                }, errors={'foo_field': 'bad_value'}
            ), ('form-group form-field field-float '
                'field-foo_field field-required has-error')
        )

    def test_info_merge_call(self):
        form = self.get_form('cms.form.res.partner')
        with mock.patch('odoo.addons.cms_form'
                        '.models.cms_form_mixin.utils.data_merge') as mocked:
            form._form_info_merge({'a': '1'}, {'b': '2'})
            mocked.assert_called_with({'a': '1'}, {'b': '2'})
