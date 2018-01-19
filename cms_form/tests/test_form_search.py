# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from .common import FormTestCase
from .utils import fake_request
from .fake_models import FakePartnerForm, FakeSearchPartnerForm


class TestCMSSearchForm(FormTestCase):

    TEST_MODELS_KLASSES = [FakePartnerForm, FakeSearchPartnerForm]

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
        cls.partner_model = cls.env['res.partner']

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

    def get_search_form(self, data):
        request = fake_request(form_data=data)
        form = self.get_form(
            'cms.form.search.res.partner', req=request)
        # restrict search results to these ids
        form.test_record_ids = self.expected_partners_ids
        form.form_process()
        return form

    def test_search(self):
        data = {'name': 'Salmo', }
        form = self.get_search_form(data)
        self.assert_results(form, 1, self.expected_partners[:1])

        data = {'name': 'Marracash', }
        form = self.get_search_form(data)
        self.assert_results(form, 1, self.expected_partners[1:2])

        data = {'country_id': self.env.ref('base.it').id, }
        form = self.get_search_form(data)
        self.assert_results(form, 2, self.expected_partners[:2])

        data = {'country_id': self.env.ref('base.fr').id, }
        form = self.get_search_form(data)
        self.assert_results(form, 1, self.expected_partners[4:])
