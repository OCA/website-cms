# -*- coding: utf-8 -*-
# Copyright 2016 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import fake_request
from .common import FormTestCase


class TestCMSForm(FormTestCase):

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
