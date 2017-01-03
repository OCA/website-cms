# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from openerp import api, fields, models


class WebsitePublishedMixin(models.AbstractModel):
    _inherit = "website.published.mixin"

    cms_delete_url = fields.Char(
        string='CMS delete URL',
        compute='_compute_cms_delete_url',
        readonly=True,
    )

    @api.multi
    def _compute_cms_delete_url(self):
        for item in self:
            item.cms_delete_url = \
                '/cms/{}/{}/delete'.format(item._name, item.id)

    cms_delete_confirm_url = fields.Char(
        string='CMS delete confirm URL',
        compute='_compute_cms_delete_confirm_url',
        readonly=True,
    )

    @api.multi
    def _compute_cms_delete_confirm_url(self):
        for item in self:
            item.cms_delete_url = \
                '/cms/{}/{}/delete/confirm'.format(item._name, item.id)

    # customize this per-model
    cms_after_delete_url = '/'
