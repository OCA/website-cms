# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import fields, models, tools
import os

# ease testing w/ pytest
testing = tools.config.get('test_enable') or \
    os.environ.get('ODOO_TEST_ENABLED')


if testing:
    class CMSNotificationPanel(models.AbstractModel):

        _inherit = 'cms.notification.panel.form'

        enable_1 = fields.Boolean(string='Enable 1')
        enable_2 = fields.Boolean(string='Enable 2')
        enable_3 = fields.Boolean(string='Enable 3')

        @property
        def _form_subtype_fields(self):
            res = super(CMSNotificationPanel, self)._form_subtype_fields
            res.update({
                'enable_1': 'cms_notification.test_subtype1',
                'enable_2': 'cms_notification.test_subtype2',
                'enable_3': 'cms_notification.test_subtype3',
            })
            return res
