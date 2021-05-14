# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class FakePartnerChannelForm(models.AbstractModel):
    """A test model form."""

    _name = "cms.form.mail.channel.partner"
    _inherit = "cms.form"
    _description = "CMS Form test partner channel form"
    # This model has `_rec_name = 'partner_id'` and allows us
    # to test a specific case for form_title computation
    _form_model = "mail.channel.partner"
