# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class FakePartnerRelModel(models.Model):
    _name = "fake.partner.related"
    _description = _name
    _rec_name = "partner_id"

    foo = fields.Char()
    partner_id = fields.Many2one("res.partner")


class FakePartnerRelatedForm(models.AbstractModel):
    """A test model form."""

    _name = "cms.form.rel.partner"
    _inherit = "cms.form"
    _description = "CMS Form test partner form"
    # This model has `_rec_name = 'partner_id'` and allows us
    # to test a specific case for form_title computation
    form_model_name = fields.Char(default=FakePartnerRelModel._name)
