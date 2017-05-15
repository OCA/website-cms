# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import fields, models


class MailMessageSubtype(models.Model):
    _inherit = 'mail.message.subtype'

    cms_type = fields.Boolean(
        'Visible in CMS control panel',
        help=("If active, this message subtype will be visible "
              "in users' notifications control panel.")
    )
