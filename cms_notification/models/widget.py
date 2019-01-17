# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class NotificationSelectionWidget(models.AbstractModel):
    _name = 'cms.form.widget.notif_radio'
    _inherit = 'cms.form.widget.radio'
    _w_template = 'cms_notification.field_widget_notification_selection'

    help_tmpl_prefix = 'cms_notification.notify_email_help_'

    @property
    def w_option_items(self):  # pragma: no cover
        """Change options order and inject help text."""
        items = []
        sel = dict(self.w_field['selection'])
        for item in ('inbox', 'email', ):
            template = self.env.ref(
                self.help_tmpl_prefix + item, raise_if_not_found=False)
            _help = None
            if template:
                _help = template.render({'sel': sel, 'field': self.w_field})
            items.append({
                'value': item,
                'label': sel[item],
                'help': _help,
            })
        return items
