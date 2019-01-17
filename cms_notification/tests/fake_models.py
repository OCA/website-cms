# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class FakeNotificationPanel(models.AbstractModel):

    _name = 'cms.notification.panel.form'
    _inherit = 'cms.notification.panel.form'

    enable_1 = fields.Boolean(string='Enable 1')
    enable_2 = fields.Boolean(string='Enable 2')
    enable_3 = fields.Boolean(string='Enable 3')

    @property
    def _form_subtype_fields(self):
        return {
            'enable_1': 'cms_notification.test_subtype1',
            'enable_2': 'cms_notification.test_subtype2',
            'enable_3': 'cms_notification.test_subtype3',
        }
