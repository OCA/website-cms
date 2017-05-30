# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import models, fields, api


class CMSPage(models.Model):
    """Model of a CMS page."""

    _name = 'cms.page'
    _description = 'CMS page'
    # _table = 'cms_page'
    _inherit = [
        'cms.content.mixin',
        'cms.parent.mixin',
        'cms.security.mixin',
    ]
    # FIXME weird: this flag should be set by `models.Model`
    # but for some reason, in security mixin
    # in `_setup_complete` this flag is false...
    _auto = True
    _auto_security_policy = True

    type_id = fields.Many2one(
        string='Page type',
        comodel_name='cms.page.type',
        default=lambda self: self._default_type_id()
    )
    view_id = fields.Many2one(
        string='View',
        comodel_name='ir.ui.view',
        domain=lambda self: self._default_view_domain(),
        default=lambda self: self._default_view_id()
    )
    sub_page_type_id = fields.Many2one(
        string='Default page type for sub pages',
        comodel_name='cms.page.type',
        help=("You can select a page type to be used "
              u"by default for each contained page."),
    )
    sub_page_view_id = fields.Many2one(
        string='Default page view for sub pages',
        comodel_name='ir.ui.view',
        help=("You can select a view to be used "
              u"by default for each contained page."),
        domain=lambda self: self._default_view_domain(),
    )
    default_view_item_id = fields.Many2one(
        string='Default view item',
        comodel_name='cms.page',
        help=("Select an item to be used as default view "
              u"for current page."),
    )

    @api.model
    def _default_type_id(self):
        return self.env['cms.page.type'].search(
            [('default', '=', True)], limit=1)

    @api.model
    def _default_view_id(self):
        page_view = self.env.ref('cms_page.page_default')
        return page_view and page_view.id or False

    @api.model
    def _default_view_domain(self):
        return [
            ('type', '=', 'qweb'),
            ('cms_view', '=', True),
        ]

    def _child_create_context(self):
        ctx = {}
        for k in ('type_id', 'view_id'):
            fname = 'sub_page_' + k
            value = getattr(self, fname)
            if value:
                ctx['default_' + k] = value.id
        return ctx

    def _open_children_context(self):
        return self._child_create_context()
