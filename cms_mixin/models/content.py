# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from openerp import models, fields, api, tools
from openerp.addons.website.models.website import slug


def to_slug(item):
    """Force usage of item.name."""
    value = (item.id, item.name)
    return slug(value)


class CMSContentMixin(models.AbstractModel):
    """Base model of a CMS content."""

    _name = 'cms.content.mixin'
    _description = 'CMS content mixin'
    _inherit = [
        'website.published.mixin',
        'cms.orderable.mixin',
        'cms.coremetadata.mixin',
    ]

    name = fields.Char(
        'Name',
        required=True,
    )
    description = fields.Text(
        'Description',
        help="Brief description of what this content is about."
    )
    body = fields.Html(
        'HTML Body',
        sanitize=False
    )

    @property
    def cms_url_prefix(self):
        """Prefix/path for your model URLs.

        You should override this to customize your model's URL.
        Of course, you should provide your own controller to handle it.
        """
        return u'/cms/content/{}/'.format(self._name)

    @api.multi
    @api.depends('name')
    def _website_url(self, name, arg):
        """Override method defined by `website.published.mixin`."""
        res = {}
        for item in self:
            res[item.id] = self.cms_url_prefix + slug(item)
        return res

    @api.multi
    def toggle_published(self):
        """Publish / Unpublish this page right away."""
        self.write({'website_published': not self.website_published})
