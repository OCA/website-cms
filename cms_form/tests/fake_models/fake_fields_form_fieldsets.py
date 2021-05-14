# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class FakeFieldsFormWithFieldsets(models.AbstractModel):
    """A test model form."""

    _name = "cms.form.test_fieldsets"
    _inherit = "cms.form.test_fields"
    _description = "CMS Form test fieldsets form"
    _form_fieldsets = [
        {"id": "main", "fields": ["a_char"]},
        {
            "id": "numbers",
            "title": "Number fields",
            "description": "Only number fields here",
            "fields": ["a_number", "a_float"],
            "css_extra_klass": "best_fieldset",
        },
        {
            "id": "relations",
            "title": "Only relations here",
            "fields": ["a_many2one", "a_many2many", "a_one2many"],
        },
        {"id": "protected", "fields": ["ihaveagroup"]},
    ]
    ihaveagroup = fields.Char(groups="website.group_website_designer")
