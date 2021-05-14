# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class FakeFieldsForm(models.AbstractModel):
    """A test model form."""

    _name = "cms.form.test_fields"
    _inherit = "cms.form"
    _description = "CMS Form test fields form"

    a_char = fields.Char()
    a_number = fields.Integer()
    a_float = fields.Float()
    # fake relation fields
    a_many2one = fields.Char()
    a_one2many = fields.Char()
    a_many2many = fields.Char()

    def _form_fields(self):
        _fields = super()._form_fields()
        # fake fields' types
        _fields["a_many2one"]["type"] = "many2one"
        _fields["a_many2one"]["relation"] = "res.partner"
        _fields["a_many2many"]["type"] = "many2many"
        _fields["a_many2many"]["relation"] = "res.partner"
        _fields["a_one2many"]["type"] = "one2many"
        _fields["a_one2many"]["relation"] = "res.partner"
        return _fields

    def _form_validate_a_float(self, value, **request_values):
        """Specific validator for `a_float` field."""
        value = float(value or "0")
        return not value > 5, "Must be greater than 5!"

    def _form_validate_char(self, value, **request_values):
        """Specific validator for all `char` fields."""
        return not len(value) > 8, "Text length must be greater than 8!"
