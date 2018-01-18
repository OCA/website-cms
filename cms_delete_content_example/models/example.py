# # Copyright 2017-2018 Rémy Taymans
# # License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ExampleModel(models.Model):
    """A demo model"""

    _name = "cms.delete.content.example"
    _inherit = "website.published.mixin"

    name = fields.Char(required=True)

    @property
    def cms_after_delete_url(self):
        return '/list-delete-content-example'
