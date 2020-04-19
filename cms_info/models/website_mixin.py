# Copyright 2018 Simone Orsi (Camptocamp)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models


class WebsiteMixin(models.AbstractModel):
    _name = "website.published.mixin"
    # Apply cms mixin to website published one
    _inherit = ["website.published.mixin", "cms.info.mixin"]
