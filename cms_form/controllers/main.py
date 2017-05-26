# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import werkzeug

from openerp import http, _
from openerp.http import request


class FormControllerMixin(object):

    # default template
    template = 'cms_form.form_wrapper'

    def get_template(self, form, **kw):
        """Retrieve rendering template.

        Defaults to `template` attribute.
        Can be overridden straight in the form
        using the attribute `form_wrapper_template`.
        """
        template = self.template

        if getattr(form, 'form_wrapper_template', None):
            template = form.form_wrapper_template

        if not template:
            raise NotImplementedError("You must provide a template!")
        return template

    def get_render_values(self, main_object, **kw):
        """Retrieve rendering values.

        You can override this to inject more values.
        """
        parent = None
        if getattr(main_object, 'parent_id', None):
            # get the parent if any
            parent = main_object.parent_id

        kw.update({
            'main_object': main_object,
            'parent': parent,
            'controller': self,
        })
        return kw

    def _can_create(self, model, raise_exception=True):
        """Check that current user can create instances of given model."""
        return request.env[model].check_access_rights(
            'create', raise_exception=raise_exception)

    def _can_edit(self, main_object, raise_exception=True):
        """Check that current user can edit given main object."""
        try:
            main_object.check_access_rights('write')
            main_object.check_access_rule('write')
            can = True
        except Exception:
            if raise_exception:
                raise
            can = False
        return can

    def form_model_key(self, model):
        """Return a valid form model."""
        return 'cms.form.' + model

    def get_form(self, model, main_object=None, **kw):
        """Retrieve form for given model or object and initialize it."""
        form_model_key = self.form_model_key(model)
        if form_model_key in request.env:
            form = request.env[form_model_key].form_init(
                request, main_object=main_object)
        else:
            # TODO: enable form by default?
            # How? with a flag on ir.model.model?
            # And which fields to include automatically?
            raise NotImplementedError(
                _('%s model has no CMS form registered.') % model
            )
        return form

    def check_permission(self, model, main_object):
        """Check permission on current model and main object."""
        if main_object:
            self._can_edit(main_object)
        else:
            self._can_create(model)

    def make_response(self, model, model_id=None, page=0, **kw):
        """Prepare and return form response.

        :param model: an odoo model's name
        :param model_id: an odoo record's id
        :param page: current page if any (mostly for search forms)
        :param kw: extra parameters

        How it works:
        * retrieve current main object if any
        * check permission on model and/or main object
        * retrieve the form
        * make the form process current request
        * if the form is successful and has `form_redirect` attribute
          it redirects to it.
        * otherwise it just renders the form
        """
        main_object = None
        if model_id:
            main_object = request.env[model].browse(model_id)
        self.check_permission(model, main_object)
        form = self.get_form(model, main_object=main_object)
        # pass only specific extra args, to not pollute form render values
        form.form_process(extra_args={'page': page})
        # search forms do not need these attrs
        if getattr(form, 'form_success', None) \
                and getattr(form, 'form_redirect', None):
            # anything went fine, redirect to next url
            return werkzeug.utils.redirect(form.form_next_url())
        # render form wrapper
        values = self.get_render_values(main_object, **kw)
        values['form'] = form
        return request.render(
            self.get_template(form, **kw),
            values,
        )


class CMSFormController(http.Controller, FormControllerMixin):
    """CMS form controller."""

    @http.route([
        '/cms/form/create/<string:model>',
        '/cms/form/edit/<string:model>/<int:model_id>',
    ], type='http', auth='user', website=True)
    def cms_form(self, model, model_id=None, **kw):
        """Handle a `form` route.
        """
        return self.make_response(model, model_id=model_id, **kw)


class SearchFormControllerMixin(FormControllerMixin):

    template = 'cms_form.search_form_wrapper'

    def form_model_key(self, model):
        return 'cms.form.search.' + model

    def check_permission(self, model, main_object):
        pass


class CMSSearchFormController(http.Controller, SearchFormControllerMixin):
    """CMS form controller."""

    @http.route([
        '/cms/form/search/<string:model>',
        '/cms/form/search/<string:model>/page/<int:page>',
    ], type='http', auth='public', website=True)
    def cms_form(self, model, **kw):
        """Handle a search `form` route.
        """
        return self.make_response(model, **kw)
