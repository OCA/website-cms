# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


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
            'country_id': {
                'id': main_object.country_id.id,
                'name': main_object.country_id.name
            },
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
        data['country_id'] = {
            'id': 7,
            'name': self.env['res.country'].browse(7).name,
        }
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
