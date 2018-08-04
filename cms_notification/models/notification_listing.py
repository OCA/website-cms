# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, _


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

    @property
    def form_title(self):  # pragma: no cover
        return _('My notifications')

    @property
    def form_description(self):  # pragma: no cover
        # no description needed, at least for now :)
        return ''

    def form_search_domain(self, search_values):
        domain = super().form_search_domain(search_values)
        default_domain = [
            ('partner_ids', 'in', [self.env.user.partner_id.id, ]),
            ('subtype_id.cms_type', '=', True),
        ]
        domain.extend(default_domain)
        return domain

    def check_view_permission(self, item):  # pragma: no cover
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
