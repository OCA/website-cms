# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from .common import fake_request, FormTestCase


class TestCMSSearchForm(FormTestCase):

    def setUp(self):
        super(TestCMSSearchForm, self).setUp()
        self.partner_model = self.env['res.partner']

        self.expected_partners = []
        self.expected_partners_ids = []
        self._expected_partners = (
            ('Salmo', self.env.ref('base.it').id, ),
            ('Marracash', self.env.ref('base.it').id, ),
            ('Notorious BIG', self.env.ref('base.us').id, ),
            ('Dr. Dre', self.env.ref('base.us').id, ),
            ('NTM', self.env.ref('base.fr').id, ),
        )

        for name, country_id in self._expected_partners:
            self.expected_partners_ids.append(self.partner_model.create({
                'name': name,
                'country_id': country_id,
            }).id)
        self.expected_partners = \
            self.partner_model.browse(self.expected_partners_ids)

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
