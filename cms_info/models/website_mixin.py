# Copyright 2018 Simone Orsi (Camptocamp)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, api, exceptions, fields


class WebsiteMixin(models.AbstractModel):
    _inherit = 'website.published.mixin'

    @property
    def cms_create_url(self):
        return '/cms/create/{}'.format(self._name)

    @property
    def cms_search_url(self):
        return '/cms/search/{}'.format(self._name)

    cms_edit_url = fields.Char(
        string='CMS edit URL',
        compute='_compute_cms_edit_url',
        readonly=True,
    )

    @api.multi
    def _compute_cms_edit_url(self):
        for item in self:
            item.cms_edit_url = '/cms/edit/{}/{}'.format(item._name, item.id)

    @api.multi
    def cms_is_owner(self, uid=None):
        self.ensure_one()
        uid = uid or self.env.user.id
        return self.create_uid.id == uid

    @api.model
    def cms_can_create(self):
        return self.check_access_rights('create', raise_exception=False)

    @api.multi
    def _cms_check_perm(self, mode):
        self.ensure_one()
        try:
            self.check_access_rights(mode)
            self.check_access_rule(mode)
            can = True
        except exceptions.AccessError:
            can = False
        return can

    def cms_can_edit(self):
        return self._cms_check_perm('write')

    def cms_can_delete(self):
        return self._cms_check_perm('unlink')

    def cms_can_publish(self):
        # TODO: improve this
        return self.cms_can_edit()

    def cms_info(self):
        info = {
            'is_owner': self.cms_is_owner(),
            'can_edit': self.cms_can_edit(),
            'can_create': self.cms_can_create(),
            'can_publish': self.cms_can_publish(),
            'can_delete': self.cms_can_delete(),
            'create_url': self.cms_create_url,
            'edit_url': self.cms_edit_url,
            # delete/delete confirm URLs come from `cms_delete_content`
            'delete_url': self.cms_delete_confirm_url,
        }
        return info
