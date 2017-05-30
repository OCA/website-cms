# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import json

from openerp import http
from openerp.http import request
import werkzeug
from werkzeug.exceptions import NotFound


class ContextAwareMixin(object):
    """`Context` aware mixin klass.

    The `context` in this case is what odoo calls `main_object`.
    """

    # default template
    template = ''

    def get_template(self, main_object, **kw):
        """Retrieve rendering template."""
        template = self.template

        if getattr(main_object, 'view_id', None):
            template = main_object.view_id.key

        if getattr(main_object, 'default_view_item_id', None):
            view_item = main_object.default_view_item_id
            if view_item.view_id:
                template = view_item.view_id.key

        if not template:
            raise NotImplementedError("You must provide a template!")
        return template

    def get_render_values(self, main_object, **kw):
        """Retrieve rendering values.

        Essentially we need 2 items: ``main_object`` and ``parent``.

        The main_object by default is the item being traversed.
        In other words: if you traverse the path to a page
        that page will be the main_object.

        The parent - if any - is always the parent of the item being traversed.

        For instance:

            /cms/page-1/page-2

        in this case, `page-2` is the main_object and `page-1` the parent.
        """
        parent = None
        if getattr(main_object, 'parent_id', None):
            # get the parent if any
            parent = main_object.parent_id

        if getattr(main_object, 'default_view_item_id', None):
            # get a default item if any
            main_object = main_object.default_view_item_id

        # for std editable variable see `ir.ui.view._prepare_qcontext`
        editable = self._can_edit(main_object)
        lang = request.env.context.get('lang')
        translatable = editable \
            and lang != request.website.default_lang_code
        editable = not translatable and editable

        kw.update({
            'main_object': main_object,
            'parent': parent,
            # override values from std qcontext
            'editable': editable,
            'translatable': translatable,
        })
        return kw

    def _can_edit(self, main_object):
        """Override this to protect the view or the item by raising errors."""
        return main_object.check_permission(mode='write')

    def render(self, main_object, **kw):
        """Retrieve parameters for rendering and render view template."""
        return request.website.render(
            self.get_template(main_object, **kw),
            self.get_render_values(main_object, **kw),
        )


# `model` is our converter that checks security
# see `website.security.mixin`.
PAGE_VIEW_ROUTES = [
    '/cms/page/<model("cms.page"):main_object>',
    '/cms/page/<model("cms.page"):main_object>/page/<int:page>',
]


class PageViewController(http.Controller, ContextAwareMixin):
    """CMS page view controller."""

    template = 'cms_page.page_default'

    @http.route(PAGE_VIEW_ROUTES, type='http', auth='public', website=True)
    def view_page(self, main_object, **kw):
        """Handle a `page` route.

        Many optional arguments come from `kw` based on routing match above.
        """
        site = request.website
        # TODO: use permission
        # check published
        # This is weird since it should be done by `website` module itself.
        # Alternatively we can put this in our `secure model` route handler.
        if not site.is_publisher() and not main_object.website_published:
            raise NotFound

        # TODO
        # if main_object.has_redirect():
        #     data = main_object.get_redirect_data()
        #     redirect = werkzeug.utils.redirect(data.url, data.status)
        #     return redirect
        if 'edit_translations' in kw:
            # for some reasons here we get an empty string
            # as value, and this breaks translation editor initialization :(
            kw['edit_translations'] = True

        # handle translations switch
        if site and 'edit_translations' not in kw \
                and not site.default_lang_code == request.lang \
                and not site.is_publisher():
            # check if there's any translation for current page in request lang
            if request.lang not in main_object.get_translations():
                raise NotFound
        return self.render(main_object, **kw)
