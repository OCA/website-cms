# Copyright 2017-2018 Camptocamp - Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import api, fields, models, _


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
                '/cms/delete/{}/{}'.format(item._name, item.id)

    cms_delete_confirm_url = fields.Char(
        string='CMS delete confirm URL',
        compute='_compute_cms_delete_confirm_url',
        readonly=True,
    )

    @api.multi
    def _compute_cms_delete_confirm_url(self):
        for item in self:
            item.cms_delete_confirm_url = \
                '/cms/delete/{}/{}/confirm'.format(item._name, item.id)

    @property
    def cms_after_delete_url(self):
        return '/'

    @api.multi
    def msg_content_delete_confirm(self):
        self.ensure_one()
        return _('Are you sure you want to delete this item?')

    @api.multi
    def msg_content_deleted(self):
        self.ensure_one()
        return _('%s deleted.') % self._description
