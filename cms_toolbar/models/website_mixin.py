# Copyright 2018 Simone Orsi - Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, api


class WebsiteMixin(models.AbstractModel):
    _inherit = 'website.published.mixin'

    _toolbar_template = 'cms_toolbar.toolbar'

    def _cms_toolbar_values(self, **kw):
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
        # override w/ custom values if needed
        values.update(kw)
        # show left actions if
        show_if = ('show_edit', 'show_publish', 'show_delete')
        values['show_left_actions'] = any([values[k] for k in show_if])
        # show right actions if
        show_if = ('show_create', )
        values['show_right_actions'] = any([values[k] for k in show_if])
        # show whole toolbar if
        show_if = ('show_left_actions', 'show_right_actions', )
        values['show_toolbar'] = any([values[k] for k in show_if])
        return values

    @api.model
    def cms_render_toolbar(self, **kw):
        if self.env.user._is_public():
            # no anon action
            return ''
        return self.env.ref(
            self._toolbar_template).render(self._cms_toolbar_values(**kw))
