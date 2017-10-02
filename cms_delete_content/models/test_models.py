# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, tools

testing = tools.config.get('test_enable')

if testing:
    class PublishResPartner(models.Model):
        _name = "res.partner"
        _inherit = ["res.partner", "website.published.mixin"]
