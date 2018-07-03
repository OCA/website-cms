# Copyright 2018 Simone Orsi - Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, api


class WebsiteMixin(models.AbstractModel):
    _inherit = 'website.published.mixin'

    _toolbar_template = 'cms_toolbar.toolbar'

    @api.model
    def cms_render_toolbar(self, **kw):
        if self.env.user._is_public():
            # no anon action
            return ''
        values = self.cms_info()
        values.update({
            'show_create': values['can_create'],
            'show_edit': self and values['can_edit'],
            'show_delete': self and values['can_delete'],
            'show_publish': self and values['can_publish'],
            'show_popover': True,
            'popover_content_template': 'cms_toolbar.popover_html_content',
            'main_object': self,
        })
        values.update(kw)
        return self.env.ref(self._toolbar_template).render(values)
