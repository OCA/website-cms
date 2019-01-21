# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from .common import FormTestCase
from .utils import fake_request
from .fake_models import (
    FakePartnerForm, FakeSearchPartnerForm, FakeSearchPartnerFormMulti
)
import mock


class TestCMSSearchForm(FormTestCase):

    TEST_MODELS_KLASSES = [
        FakePartnerForm,
        FakeSearchPartnerForm,
        FakeSearchPartnerFormMulti,
    ]

    @classmethod
    def setUpClass(cls):
        super(TestCMSSearchForm, cls).setUpClass()
        cls._setup_models()
        cls._setup_records()

    @classmethod
    def tearDownClass(cls):
        cls._teardown_models()
        super(TestCMSSearchForm, cls).tearDownClass()

    @classmethod
    def _setup_records(cls):
        cls.partner_model = cls.env['res.partner'].with_context(
            tracking_disable=True)

        cls.expected_partners = []
        cls.expected_partners_ids = []
        cls._expected_partners = (
            ('Salmo', cls.env.ref('base.it').id, ),
            ('Marracash', cls.env.ref('base.it').id, ),
            ('Notorious BIG', cls.env.ref('base.us').id, ),
            ('Dr. Dre', cls.env.ref('base.us').id, ),
            ('NTM', cls.env.ref('base.fr').id, ),
        )

        for name, country_id in cls._expected_partners:
            cls.expected_partners_ids.append(cls.partner_model.create({
                'name': name,
                'country_id': country_id,
            }).id)
        cls.expected_partners = \
            cls.partner_model.browse(cls.expected_partners_ids)

    def assert_results(self, form, count, expected):
        self.assertTrue('results' in form.form_search_results)
        self.assertTrue('count' in form.form_search_results)
        self.assertTrue('pager' in form.form_search_results)
        self.assertEqual(len(form.form_search_results['results']), count)
        self.assertEqual(form.form_search_results['count'], count)
        self.assertEqual(
            sorted(form.form_search_results['results'].mapped('id')),
            sorted(expected.mapped('id')),
        )

    def get_search_form(
            self, data, form_model='cms.form.search.res.partner', **kw):
        request = fake_request(form_data=data)
        form = self.get_form(form_model, req=request, **kw)
        # restrict search results to these ids
        form.test_record_ids = self.expected_partners_ids
        return form

    def test_form_base_attrs(self):
        form = self.get_search_form({})
        self.assertEqual(form.form_mode, 'search')
        self.assertEqual(form.form_title, 'Search Contact')

    def test_search_domain(self):
        form = self.get_search_form({})
        form.test_record_ids = []
        form._form_search_domain_rules = {
            'float_field': lambda field, value, search_values: (
                'float_field', '>', value
            )
        }

        def mock_fields(form):
            return {
                'char_field': {
                    'type': 'char',
                },
                'text_field': {
                    'type': 'text',
                },
                'int_field': {
                    'type': 'integer',
                },
                'float_field': {
                    'type': 'float',
                },
                'm2o_field': {
                    'type': 'many2one',
                },
                'bool_field': {
                    'type': 'boolean',
                },
                'date_field': {
                    'type': 'date',
                },
                'datetime_field': {
                    'type': 'date',
                },
                'o2m_field': {
                    'type': 'one2many',
                },
                'm2m_field': {
                    'type': 'many2many',
                },
            }
        with mock.patch.object(type(form), 'form_fields', mock_fields):
            search_values = {
                'char_field': 'foo',
                'text_field': '',
                'int_field': 2,
                'float_field': 1.0,
                'm2o_field': 3,
                'bool_field': 'on',
                'date_field': '2019-01-26',
                'datetime_field': '',
                'o2m_field': [1, 2, 3],
                'm2m_field': '',
            }
            expected = [
                ('char_field', 'ilike', '%foo%'),
                ('int_field', '=', 2),
                ('float_field', '>', 1.0),
                ('m2o_field', '=', 3),
                ('bool_field', '=', True),
                ('date_field', '=', '2019-01-26'),
                ('o2m_field', 'in', [1, 2, 3]),
            ]
            self.assertEqual(
                sorted(form.form_search_domain(search_values)),
                sorted(expected),
            )

    def test_search(self):
        data = {'name': 'Salmo', }
        form = self.get_search_form(data)
        form.form_process()
        self.assert_results(form, 1, self.expected_partners[:1])

        data = {'name': 'Marracash', }
        form = self.get_search_form(data)
        form.form_process()
        self.assert_results(form, 1, self.expected_partners[1:2])

        data = {'country_id': self.env.ref('base.it').id, }
        form = self.get_search_form(data)
        form.form_process()
        self.assert_results(form, 2, self.expected_partners[:2])

        data = {'country_id': self.env.ref('base.fr').id, }
        form = self.get_search_form(data)
        form.form_process()
        self.assert_results(form, 1, self.expected_partners[4:])

        data = {'name': '', 'country_id': self.env.ref('base.fr').id, }
        form = self.get_search_form(data)
        form.form_process()
        self.assert_results(form, 1, self.expected_partners[4:])

    def test_search_no_result(self):
        form = self.get_search_form({}, show_results_no_submit=False)
        form.form_process()
        self.assertEqual(form.form_search_results, {})

    def test_pager_url(self):
        data = {'name': 'Salmo', }
        form = self.get_search_form(data)
        # value from rendering
        render_values = {'extra_args': {'pager_url': '/foo'}}
        self.assertEqual(
            form._form_get_url_for_pager(render_values),
            '/foo'
        )
        # value from model's `cms_search_url` if available
        form = self.get_search_form(data)
        # add fake cms_search_url on current model
        # NOTE: when website_partner is installed this mocking is useless
        # but we need it here just to demonstrate we are handling it
        with mock.patch.object(
            type(form.form_model),
            'cms_search_url',
            property(lambda x: '/cms/search/res.partner'),
            create=True,
        ):
            self.assertEqual(
                form._form_get_url_for_pager({}),
                '/cms/search/res.partner'
            )
        # value from request path
        request = fake_request(url='/search/custom/page/1?foo=baz')
        form = self.get_form('cms.form.search.res.partner', req=request)
        # on the contrary, here, we make sure `cms_search_url` is empty
        # so that the default via request path is used
        with mock.patch.object(
            type(form.form_model),
            'cms_search_url',
            property(lambda x: ''),
            create=True,
        ):
            self.assertEqual(
                form._form_get_url_for_pager({}),
                '/search/custom'
            )

    def test_search_multi(self):
        countries = [
            self.env.ref('base.it').id,
            self.env.ref('base.fr').id,
        ]
        data = {'country_id': ','.join(map(str, countries))}
        form = self.get_search_form(
            data, form_model='cms.form.search.res.partner.multicountry')
        form.form_process()
        expected = self.expected_partners.filtered(
            lambda x: x.country_id.id in countries)
        self.assert_results(form, 3, expected)

    def test_search_form_bypass_security_check(self):
        form = self.get_search_form(
            {}, sudo_uid=self.env.ref('base.public_user').id)
        self.assertTrue(form.form_check_permission())

    def test_search_custom_rules(self):
        data = {'country_id': 'Italy', }
        form = self.get_search_form(data)
        form.form_process()
        # we find them all since domain is mocked to include all test partners
        self.assert_results(form, 5, self.expected_partners)
        # apply custom rules
        data = {'country_id': 'Italy', }
        form = self.get_search_form(data, search_domain_rules={
            'country_id': ('country_id.name', 'ilike', '')
        })
        form.form_process()
        self.assert_results(form, 2, self.expected_partners[:2])
