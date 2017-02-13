# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models
from openerp import fields


class ExamplePartnerForm(models.AbstractModel):
    """A test model form."""

    _name = 'cms.form.res.partner'
    _inherit = 'cms.form'
    _form_model = 'res.partner'
    _form_model_fields = ('name', 'country_id')
    _form_required_fields = ('name', )
    _form_fields_order = ('name', 'country_id')

    custom = fields.Char()

    def _form_load_custom(
            self, form, main_object, fname, value, **req_values):
        return req_values.get('custom', 'oh yeah!')
