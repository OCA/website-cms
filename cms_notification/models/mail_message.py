# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, fields, api, tools


class MailMessage(models.Model):
    _inherit = 'mail.message'

    ref_item_id = fields.Reference(
        string="Referenced item",
        selection="_selection_ref_item_id",
        compute="_compute_ref_item_id",
        readonly=True,
    )
    ref_model_id = fields.Many2one(
        string="Referenced model",
        comodel_name="ir.model",
        compute="_compute_ref_model_id",
    )

    @api.model
    @tools.ormcache("self")
    def _selection_ref_item_id(self):
        """Allow any model; after all, this field is readonly."""
        return [(r.model, r.name) for r in self._reference_models_search()]

    @api.multi
    @api.depends("model", "res_id")
    def _compute_ref_item_id(self):
        for item in self:
            if item.model and item.res_id:
                item.ref_item_id = "{},{}".format(item.model, item.res_id)

    @api.multi
    @api.depends("model")
    def _compute_ref_model_id(self):
        for item in self:
            if item.model:
                item.ref_model_id = self.env['ir.model'].search(
                    [('model', '=', item.model)], limit=1
                )

    def _reference_models_search(self):
        return self.env["ir.model"].search([])

    def _get_notifications(self, partner_id, is_read=False):
        return self.env['mail.notification'].sudo().search([
            ('mail_message_id', 'in', self.ids),
            ('res_partner_id', '=', partner_id),
            ('is_read', '=', is_read)
        ])

    def is_unread(self, partner=None):
        partner = partner or self.env.user.partner_id
        return bool(self._get_notifications(partner.id))

    def is_read(self, partner=None):
        partner = partner or self.env.user.partner_id
        return bool(self._get_notifications(partner.id, is_read=True))

    # TODO: explain why we need this override!

    # @api.multi
    # def mark_as_unread(self, channel_ids=None):
    #     """ Add needactions to messages for the current partner. """
    #     partner_id = self.env.user.partner_id.id
    #     for message in self:
    #         message.write({'needaction_partner_ids': [(4, partner_id)]})

    #     ids = [m.id for m in self]
    #     notification = {'type': 'mark_as_unread',
    #     'message_ids': ids, 'channel_ids': channel_ids}
    #     self.env['bus.bus'].sendone(
    #         (self._cr.dbname, 'res.partner', 
    #         self.env.user.partner_id.id), notification)

    @api.multi
    def mark_as_unread(self, channel_ids=None):
        partner_id = self.env.user.partner_id.id
        notifs = self._get_notifications(partner_id, is_read=True)
        notifs.write({'is_read': False})
        notification = {
            'type': 'mark_as_unread',
            'message_ids': self.ids,
            'channel_ids': channel_ids
        }
        self.env['bus.bus'].sendone((
            self.env.cr.dbname,
            'res.partner', 
            partner_id
        ), notification)


