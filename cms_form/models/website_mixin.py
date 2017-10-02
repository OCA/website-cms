# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class WebsitePublishedMixin(models.AbstractModel):
    _inherit = "website.published.mixin"

    @property
    def cms_add_url(self):
        return '/cms/form/create/{}'.format(self._name)

    @property
    def cms_search_url(self):
        return '/cms/form/search/{}'.format(self._name)

    cms_edit_url = fields.Char(
        string='CMS edit URL',
        compute='_compute_cms_edit_url',
        readonly=True,
    )

    @api.multi
    def _compute_cms_edit_url(self):
        for item in self:
            item.cms_edit_url = \
                '/cms/form/edit/{}/{}'.format(item._name, item.id)
