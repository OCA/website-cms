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

    # TODO: shall we check if the partner is a recipient?
    def is_unread(self, partner=None):
        partner = partner or self.env.user.partner_id
        return partner in self.needaction_partner_ids

    def is_read(self, partner=None):
        partner = partner or self.env.user.partner_id
        return partner not in self.needaction_partner_ids
