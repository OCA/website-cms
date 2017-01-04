# -*- coding: utf-8 -*-

from openerp import models, tools

testing = tools.config.get('test_enable')

if testing:
    class PublishResPartner(models.Model):
        _name = "res.partner"
        _inherit = ["res.partner", "website.published.mixin"]
