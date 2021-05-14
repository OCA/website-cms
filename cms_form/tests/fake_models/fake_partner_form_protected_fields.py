# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class FakePartnerFormProtectedFields(models.AbstractModel):
    """A test model form w/ `groups` protected fields."""

    _name = "cms.form.protected.fields"
    _inherit = "cms.form"
    _description = "CMS Form test partner protected fields form"
    # we'll test specifically that ordering won't break
    _form_fields_order = ["ihaveagroup", "nogroup"]

    nogroup = fields.Char()
    ihaveagroup = fields.Char(groups="website.group_website_designer")
