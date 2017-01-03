# -*- coding: utf-8 -*-
# Copyright 2016 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models
from openerp import fields


class TestPartnerForm(models.AbstractModel):
    """A test model form."""

    _name = 'cms.form.test_partner'
    _inherit = 'cms.form'
    _form_model = 'res.partner'
    _form_model_fields = ('name', 'country_id')
    _form_required_fields = ('name', 'country_id')

    custom = fields.Char()

    def _form_load_custom(self, main_object, fname, value, **req_values):
        return req_values.get('custom', 'oh yeah!')


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

    def form_fields(self):
        _fields = super(TestFieldsForm, self).form_fields()
        # fake fields' types
        _fields['a_many2one']['type'] = 'many2one'
        _fields['a_many2many']['type'] = 'many2many'
        _fields['a_one2many']['type'] = 'one2many'
        return _fields

    def _form_validate_a_float(self, value, **request_values):
        """Specific validator for `a_float` field."""
        value = float(value or '0')
        return not value > 5, 'Must be greater than 5!'

    def _form_validate_char(self, value, **request_values):
        """Specific validator for all `char` fields."""
        return not len(value) > 8, 'Text lenght must be greater than 8!'
