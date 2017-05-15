# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import models, _


class CMSNotificationListing(models.AbstractModel):
    """Hold users notifications settings."""
    _name = 'cms.notification.listing'
    _inherit = 'cms.form.search'
    _description = 'CMS notification'

    _form_model = 'mail.message'
    _form_model_fields = (
        'subtype_id',
    )
    form_search_results_template = 'cms_notification.listing'
    # form_wrapper_template = 'cms_notification.notifications_wrapper'
    # form_template = 'cms_notification.notifications_search_form'

    @property
    def form_title(self):
        return _('My notifications')

    @property
    def form_description(self):
        return ''

    @property
    def _super(self):
        return super(CMSNotificationListing, self)

    def form_search_domain(self, search_values):
        domain = self._super.form_search_domain(search_values)
        default_domain = [
            ('partner_ids', 'in', [self.env.user.partner_id.id, ]),
            ('subtype_id.cms_type', '=', True),
        ]
        domain.extend(default_domain)
        return domain

    def check_view_permission(self, item):
        """Check read permission on given item.

        We could list messages that are attached to other records.
        If the permissions for this records has changed
        then the user viewing the notification may not have
        permissions to read it anymore.
        """
        try:
            item.check_access_rights('read')
            item.check_access_rule('read')
            return True
        except:
            return False
