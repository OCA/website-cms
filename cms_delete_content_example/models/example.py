# -*- coding: utf-8 -*-
# # Copyright 2017 Rémy Taymans
# # License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ExampleModel(models.Model):
    """A test model"""

    _name = "cms.delete.content.example"
    _inherit = "website.published.mixin"

    name = fields.Char(required=True)

    @property
    def cms_after_delete_url(self):
        return '/list-delete-content-example'
