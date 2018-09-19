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
        notification_model = self.env['mail.notification']
        for item in self:
            if not item.partner_id:
                continue
            domain = [
                ('res_partner_id', '=', item.partner_id.id),
                ('mail_message_id.subtype_id.cms_type', '=', True),
                ('is_read', '=', False),
            ]
            item.has_unread_notif = bool(
                notification_model.search(domain, limit=1)
            )
