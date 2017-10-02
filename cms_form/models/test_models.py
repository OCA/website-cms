# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, tools
import os

testing = tools.config.get('test_enable') or os.environ.get('ODOO_TEST_ENABLE')

if testing:
    class TestPartnerForm(models.AbstractModel):
        """A test model form."""

        _name = 'cms.form.res.partner'
        _inherit = 'cms.form'
        _form_model = 'res.partner'
        _form_model_fields = ('name', 'country_id')
        _form_required_fields = ('name', 'country_id')

        custom = fields.Char()

        def _form_load_custom(
                self, main_object, fname, value, **req_values):
            return req_values.get('custom', 'oh yeah!')

    class TestSearchPartnerForm(models.AbstractModel):
        """A test model search form."""

        _name = 'cms.form.search.res.partner'
        _inherit = 'cms.form.search'
        _form_model = 'res.partner'
        _form_model_fields = ('name', 'country_id')

        def form_search_domain(self, search_values):
            """Force domain to include only test-created records."""
            domain = super(
                TestSearchPartnerForm, self
            ).form_search_domain(search_values)
            # we use this attr in tests to limit search results
            # to test records' scope
            include_only_ids = getattr(self, 'test_record_ids', [])
            if include_only_ids:
                domain.append(('id', 'in', include_only_ids))
            return domain

    class TestFieldsForm(models.AbstractModel):
        """A test model form."""

        _name = 'cms.form.test_fields'
        _inherit = 'cms.form'

        a_char = fields.Char()
        a_number = fields.Integer()
        a_float = fields.Float()
        # fake relation fields
        a_many2one = fields.Char()
        a_one2many = fields.Char()
        a_many2many = fields.Char()

        def _form_fields(self):
            _fields = super(TestFieldsForm, self)._form_fields()
            # fake fields' types
            _fields['a_many2one']['type'] = 'many2one'
            _fields['a_many2one']['relation'] = 'res.partner'
            _fields['a_many2many']['type'] = 'many2many'
            _fields['a_many2many']['relation'] = 'res.partner'
            _fields['a_one2many']['type'] = 'one2many'
            _fields['a_one2many']['relation'] = 'res.partner'
            return _fields

        def _form_validate_a_float(self, value, **request_values):
            """Specific validator for `a_float` field."""
            value = float(value or '0')
            return not value > 5, 'Must be greater than 5!'

        def _form_validate_char(self, value, **request_values):
            """Specific validator for all `char` fields."""
            return not len(value) > 8, 'Text lenght must be greater than 8!'
