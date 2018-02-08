# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, _


class CMSFormSearch(models.AbstractModel):
    _name = 'cms.form.search'
    _inherit = 'cms.form.mixin'

    form_buttons_template = 'cms_form.search_form_buttons'
    form_search_results_template = 'cms_form.search_results'
    form_action = ''
    form_method = 'GET'
    # you might want to just list items based on a predefined query
    # if this flag is false the search form won't be rendered
    form_show_search_form = True
    _form_mode = 'search'
    _form_extract_value_mode = 'read'
    # show results if no query has been submitted?
    _form_show_results_no_submit = 1
    _form_results_per_page = 10
    # sort by this param, defaults to model's `_order`
    _form_results_orderby = ''

    def form_update_fields_attributes(self, _fields):
        """No field should be mandatory."""
        super().form_update_fields_attributes(_fields)
        for fname, field in _fields.items():
            field['required'] = False

    __form_search_results = {}

    @property
    def form_search_results(self):
        """Return search results."""
        return self.__form_search_results

    @form_search_results.setter
    def form_search_results(self, value):
        self.__form_search_results = value

    @property
    def form_title(self):
        title = _('Search')
        if self._form_model:
            model = self.env['ir.model'].sudo().search(
                [('model', '=', self._form_model)])
            name = model and model.name or ''
            title = _('Search %s') % name
        return title

    def form_process_GET(self, render_values):
        self.form_search(render_values)
        return render_values

    def form_search(self, render_values):
        """Produce search results."""
        search_values = self.form_extract_values()
        if not search_values and not self._form_show_results_no_submit:
            return self.form_search_results
        domain = self.form_search_domain(search_values)
        count = self.form_model.search_count(domain)
        page = render_values.get('extra_args', {}).get('page', 0)
        url = render_values.get('extra_args', {}).get('pager_url', '')
        if self._form_model:
            url = getattr(self.form_model, 'cms_search_url', url)
        pager = self._form_results_pager(count=count, page=page, url=url)
        order = self._form_results_orderby or None
        results = self.form_model.search(
            domain,
            limit=self._form_results_per_page,
            offset=pager['offset'],
            order=order
        )
        self.form_search_results = {
            'results': results,
            'count': count,
            'pager': pager,
        }
        return self.form_search_results

    def pager(self, **kw):
        return self.env['website'].pager(**kw)

    def _form_results_pager(self, count=None, page=0, url='', url_args=None):
        """Prepare pager for current search."""
        url_args = url_args or self.request.args.to_dict()
        count = count
        return self.pager(
            url=url,
            total=count,
            page=page,
            step=self._form_results_per_page,
            scope=self._form_results_per_page,
            url_args=url_args
        )

    def form_search_domain(self, search_values):
        """Build search domain."""
        domain = []
        for fname, field in self.form_fields().items():
            value = search_values.get(fname)
            if value is None:
                continue
            if field['type'] in ('many2one', ) and value < 1:
                # we need an existing ID here ( > 0)
                continue
            # TODO: find the way to properly handle this.
            # It would be nice to guess leafs in a clever way.
            operator = '='
            if field['type'] in ('char', 'text'):
                operator = 'ilike'
                value = '%{}%'.format(value)
            elif field['type'] in ('integer', 'float', 'many2one'):
                operator = '='
            elif field['type'] in ('one2many', 'many2many'):
                if not value:
                    continue
                operator = 'in'
            elif field['type'] in ('many2one', ) and not value:
                # we need an existing ID here ( > 0)
                continue
            elif field['type'] in ('boolean', ):
                value = value == 'on' and True
            leaf = (fname, operator, value)
            domain.append(leaf)
        return domain
