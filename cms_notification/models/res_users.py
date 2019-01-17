# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    has_unread_notif = fields.Boolean(
        string='Has unread notif',
        compute='_compute_has_unread_notif',
        readonly=True,
    )

    @api.multi
    @api.depends()
    def _compute_has_unread_notif(self):
        msg_model = self.env['mail.message']
        for item in self:
            domain = [
                ('partner_ids', 'in', item.partner_id.id),
                ('needaction_partner_ids', 'in', item.partner_id.id),
                ('subtype_id.cms_type', '=', True),
            ]
            item.has_unread_notif = bool(msg_model.search(domain, limit=1))
