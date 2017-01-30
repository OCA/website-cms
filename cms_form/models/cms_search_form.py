# -*- coding: utf-8 -*-
# Copyright 2016 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models
from openerp import _


class CMSFormSearch(models.AbstractModel):
    _name = 'cms.form.search'
    _inherit = 'cms.form.mixin'

    form_template = 'cms_form.search_form'
    form_search_results_template = 'cms_form.search_results'
    form_action = ''
    form_method = 'GET'
    _form_mode = 'search'
    # show results if no query has been submitted?
    _form_show_results_no_submit = 1
    __form_search_results = []

    def form_update_fields_attributes(self, _fields):
        """No field should be mandatory."""
        super(CMSFormSearch, self).form_update_fields_attributes(_fields)
        for fname, field in _fields.iteritems():
            field['required'] = False

    @property
    def form_search_results(self):
        return self.__form_search_results

    @form_search_results.setter
    def form_search_results(self, value):
        self.__form_search_results = value

    @property
    def form_title(self):
        title = _('Search')
        if self._form_model:
            model = self.env['ir.model'].search(
                [('model', '=', self._form_model)])
            name = model and model.name or ''
            title = _('Search %s') % name
        return title

    def form_process_GET(self, render_values):
        self.form_search_results = self.form_search()
        return render_values

    def form_search(self):
        """Produce search results."""
        search_values = self.form_extract_values()
        if not search_values and not self._form_show_results_no_submit:
            return []
        domain = self.form_search_domain(search_values)
        results = self.form_model.search(domain)
        print domain, results
        return results

    def form_search_domain(self, search_values):
        """Build search domain.

        TODO...
        """
        domain = []
        for fname, field in self.form_fields().iteritems():
            value = search_values.get(fname)
            if value is None:
                continue
            # TODO: find the way to properly handle this
            operator = '='
            if field['type'] in ('char', 'text'):
                operator = 'ilike'
                value = '%{}%'.format(value)
            elif field['type'] in ('integer', 'float', 'many2one'):
                operator = '='
            elif field['type'] in ('one2many', 'many2many'):
                operator = 'in'
            leaf = (fname, operator, value)
            domain.append(leaf)
        return domain