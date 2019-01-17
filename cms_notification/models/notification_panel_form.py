# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, _
from odoo.addons.cms_form.utils import string_to_bool


class CMSNotificationPanel(models.AbstractModel):
    """Hold users notifications settings."""
    _name = 'cms.notification.panel.form'
    _inherit = 'cms.form'
    _description = 'CMS notification control panel'

    _form_model = 'res.users'
    _form_model_fields = (
        'notification_type',
        'digest_mode',
        'digest_frequency',
    )

    @property
    def form_title(self):  # pragma: no cover
        return _('Notification settings.')

    @property
    def form_description(self):  # pragma: no cover
        # no description needed, at least for now :)
        return ''

    @property
    def form_msg_success_updated(self):  # pragma: no cover
        return _('Changes applied.')

    def form_next_url(self, main_object=None):
        if self.request.args.get('redirect'):
            # redirect overridden
            return self.request.args.get('redirect')
        return '/my/settings/notifications'

    @property
    def form_widgets(self):
        return {
            'notification_type': 'cms.form.widget.notif_radio',
        }

    def _form_master_slave_info(self):  # pragma: no cover
        info = super()._form_master_slave_info()
        info.update({
            'notification_type': {
                'hide': {
                    'digest_mode': ('inbox', ),
                    'digest_frequency': ('inbox', ),
                },
                'show': {
                    'digest_mode': ('email', ),
                    'digest_frequency': ('email', ),
                },
            },
            'digest_mode': {
                'readonly': {
                    'digest_frequency': (False, ),
                },
                'no_readonly': {
                    'digest_frequency': (True, ),
                },
            }
        })
        return info

    @property
    def _form_subtype_fields(self):  # pragma: no cover
        """Return mapping from boolean form field to subtype xmlid.

        CMS form does not support o2m fields in an advanced way
        so we cannot add/remove/edit `notify_conf_ids` easily.

        Furthermore, we want to automatically show just checkboxes
        to enable/disable subtypes in an handy way.

        Hence, you are supposed to add a boolean field + a mapping
        field:subtype that allows to enable/disable it on the partner.
        This and the following methods take care of this.
        """
        return {
            # mapping:
            # 'your_boolean_field_name': 'your_subtype_xmlid',
        }

    def form_get_loader(self, fname, field,
                        main_object=None, value=None, **req_values):
        """Override to provide automatic loader for boolean fields."""
        loader = super().form_get_loader(
            fname, field, main_object=main_object,
            value=value, **req_values
        )
        if fname in self._form_subtype_fields.keys():
            loader = self._form_load_subtype_conf_loader
        return loader

    def _form_load_subtype_conf_loader(
            self, fname, field, value, **req_values):
        """Automatically load value for subtype conf fields."""
        if fname in req_values:
            value = string_to_bool(req_values.get(fname))
        else:
            subtype = self.env.ref(self._form_subtype_fields[fname])
            explicitly_enabled = \
                subtype in self.main_object.enabled_notify_subtype_ids
            explicitly_disabled = \
                subtype in self.main_object.disabled_notify_subtype_ids
            # mail_digest machinery will send you emails in this 2 cases:
            # * you've enabled notification explicitly
            # * you have no specific settings for the subtype
            # (hence you did not disabled it)
            value = explicitly_enabled or not explicitly_disabled

        return value

    def form_after_create_or_update(self, values, extra_values):
        """Update subtype configuration for `_form_subtype_fields`."""
        super().form_after_create_or_update(values, extra_values)
        for fname, subtype_xmlid in self._form_subtype_fields.items():
            value = extra_values.get(fname)
            subtype = self.env.ref(subtype_xmlid)
            # use sudo as we don't know if the user
            # has been allowed to update its own partner
            # and sincerely, we don't care in this case.
            self.main_object.sudo()._notify_update_subtype(subtype, value)
