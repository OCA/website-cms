# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import models, fields


class CMSPageType(models.Model):
    """Model of a CMS page type."""

    _name = 'cms.page.type'
    _description = 'CMS page type'

    name = fields.Char('Name', translate=True)
    default = fields.Boolean('Default')
