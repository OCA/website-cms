# -*- coding: utf-8 -*-

from openerp import models, fields


class WebsiteMenu(models.Model):
    """Override to add reference to cms_page."""

    _inherit = "website.menu"

    cms_page_id = fields.Many2one(
        string='CMS Page',
        comodel_name='cms.page'
    )
