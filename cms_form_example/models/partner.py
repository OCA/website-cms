# Copyright 2017 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo import fields
from odoo import tools

testing = tools.config.get('test_enable')


if not testing:
    # prevent these forms to be registered when running tests

    class ExamplePartnerForm(models.AbstractModel):
        """A test model form."""

        _name = 'cms.form.res.partner'
        _inherit = 'cms.form'
        _form_model = 'res.partner'
        _form_model_fields = ('name', 'country_id', 'category_id')
        _form_required_fields = ('name', )
        _form_fields_order = ('name', 'country_id', 'category_id')

        custom = fields.Char()

        def _form_load_custom(
                self, form, main_object, fname, value, **req_values):
            """Load a custom default for the field 'custom'."""
            return req_values.get('custom', 'oh yeah!')

    class PartnerSearchForm(models.AbstractModel):
        """Partner model search form."""

        _name = 'cms.form.search.res.partner'
        _inherit = 'cms.form.search'
        _form_model = 'res.partner'
        _form_model_fields = ('name', 'country_id', )

    class PartnerSearchFormAjax(models.AbstractModel):
        """Partner model search form with ajax."""
        _inherit = 'cms.form.search.res.partner'
        _name = 'cms.form.search.res.partner.ajax'
        _form_ajax = True
        _form_ajax_onchange = True

    class ExamplePartnerFormWithFieldsets(models.AbstractModel):
        _name = 'cms.form.res.partner.fset'
        _inherit = 'cms.form.res.partner'

        _form_fieldsets = [
            {
                'id': 'main',
                'title': 'Main',
                'fields': [
                    'name',
                    'category_id',
                ],
            },
            {
                'id': 'secondary',
                'title': 'Secondary',
                'fields': [
                    'country_id',
                ],
            },
        ]

    class ExamplePartnerFormWithTabbedFieldsets(models.AbstractModel):
        _name = 'cms.form.res.partner.fset.tabbed'
        _inherit = 'cms.form.res.partner.fset'
        _form_fieldsets_display = 'tabs'

        def _form_master_slave_info(self):
            info = super()._form_master_slave_info()
            info.update({
                'category_id': {
                    'hide': {
                        'country_id': 'form.category_id == "5"',
                    },
                    'show': {
                        'country_id': 'form.category_id != "5"',
                    },
                },
                'name': {
                    'readonly': {
                        'category_id': 'form.name == "YourCompany"',
                    },
                    'no_readonly': {
                        'category_id': 'form.name == "YourCompany2"',
                    },
                },
            })
            return info
