# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from .common import FormTestCase
from .utils import fake_request
from .fake_models import (
    FakePartnerForm, FakeSearchPartnerForm, FakeSearchPartnerFormMulti
)


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
