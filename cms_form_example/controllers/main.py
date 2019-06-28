# Copyright 2017 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.addons.cms_form.controllers.main import SearchFormControllerMixin
from odoo.addons.cms_form.controllers.main import FormControllerMixin


class PartnerForm(http.Controller, FormControllerMixin):
    """Partner form controller."""

    @http.route([
        '/partner/add',
        '/partner/<model("res.partner"):main_object>/edit',
    ], type='http', auth='user', website=True)
    def cms_form(self, main_object=None, **kw):
        """Handle a `form` route.
        """
        model = 'res.partner'
        return self.make_response(
            model, model_id=main_object and main_object.id, **kw)


class PartnerFormFieldset(http.Controller, FormControllerMixin):
    """Partner form w/ fieldsets."""

    @http.route([
        '/partner/fieldset/add',
        '/partner/fieldset/<model("res.partner"):main_object>/edit',
    ], type='http', auth='user', website=True)
    def cms_form(self, main_object=None, **kw):
        model = 'res.partner'
        return self.make_response(
            model, model_id=main_object and main_object.id, **kw)

    def form_model_key(self, model, **kw):
        """Return a valid form model."""
        return 'cms.form.res.partner.fset'


class PartnerFormTabbedFieldset(http.Controller, FormControllerMixin):
    """Partner form w/ tabs."""

    @http.route([
        '/partner/tabbed/add',
        '/partner/tabbed/<model("res.partner"):main_object>/edit',
    ], type='http', auth='user', website=True)
    def cms_form(self, main_object=None, **kw):
        model = 'res.partner'
        return self.make_response(
            model, model_id=main_object and main_object.id, **kw)

    def form_model_key(self, model, **kw):
        """Return a valid form model."""
        return 'cms.form.res.partner.fset.tabbed'


class PartnerListing(http.Controller, SearchFormControllerMixin):
    """Partner search form controller."""

    @http.route([
        '/partners',
        '/partners/page/<int:page>',
    ], type='http', auth="public", website=True)
    def market(self, **kw):
        model = 'res.partner'
        return self.make_response(model, **kw)


class PartnerListingAjax(http.Controller, SearchFormControllerMixin):
    """Partner search form controller."""

    @http.route([
        '/partnersAjax',
        '/partnersAjax/page/<int:page>',
    ], type='http', auth="public", website=True)
    def list(self, **kw):
        model = 'res.partner'
        return self.make_response(model, **kw)

    def form_model_key(self, model, **kw):
        return 'cms.form.search.' + model + '.ajax'
