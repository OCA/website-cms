# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models
from odoo.tools import pycompat

from odoo.addons.portal.controllers.portal import pager as portal_pager

from .fields import Serialized


class CMSFormSearch(models.AbstractModel):
    _name = "cms.form.search"
    _description = "CMS Form search"
    _inherit = "cms.form.mixin"

    # change defaults
    form_buttons_template = fields.Char(
        form_tech=True, default="cms_form.search_form_buttons"
    )
    form_search_results_template = fields.Char(
        form_tech=True, default="cms_form.search_results"
    )
    form_no_search_results_template = fields.Char(
        form_tech=True, default="cms_form.no_search_results"
    )
    form_method = fields.Char(form_tech=True, default="GET")
    # you might want to just list items based on a predefined query
    # if this flag is false the search form won't be rendered
    form_show_search_form = fields.Boolean(form_tech=True, default=True)
    form_mode = fields.Char(form_tech=True, default="search")
    form_extract_value_mode = fields.Char(form_tech=True, default="read")
    # show results if no query has been submitted?
    form_show_search_form = fields.Boolean(form_tech=True, default=True)
    form_show_results_no_submit = fields.Boolean(form_tech=True, default=True)
    form_results_per_page = fields.Integer(form_tech=True, default=10)
    # sort by this param, defaults to model's `_order`
    form_results_orderby = fields.Char(form_tech=True, default="")
    # declare fields that must be searched w/ multiple values
    form_search_fields_multi = Serialized(form_tech=True, default=[])
    # declare custom domain computation rules
    # opt 1: `field name: (leaf field name, operator, format value)`
    # `format_value` is a formatting compatible string
    # 'product_id': ('product_id.name', 'ilike', '{}')
    # opt 2: function that give back `(fname, operator, value)``
    # 'foo': lambda field, value, search_values: ('foo', 'not like', value)
    form_search_domain_rules = fields.Binary(form_tech=True, default={}, store=False)
    form_search_results = fields.Binary(form_tech=True, default={}, store=False)

    # make it computed
    form_title = fields.Char(form_tech=True, compute="_compute_form_title")
    form_no_result_msg = fields.Char(
        form_tech=True, compute="_compute_form_no_result_msg"
    )

    def _get_form_mode(self):
        return "search"

    def _compute_form_title(self):
        for rec in self:
            rec.form_title = rec._get_form_title()

    def _get_form_title(self):
        title = _("Search")
        if self.form_model_name:
            model = self.env["ir.model"]._get(self.form_model_name)
            name = model and model.name or ""
            title = _("Search %s") % name
        return title

    def _compute_form_no_result_msg(self):
        for rec in self:
            rec.form_no_result_msg = rec._get_form_no_result_msg()

    def _get_form_no_result_msg(self):
        return _("No items")

    def form_check_permission(self):
        """Just searching, nothing to check here."""
        return True

    def form_update_fields_attributes(self, _fields):
        """No field should be mandatory."""
        res = super().form_update_fields_attributes(_fields)
        for _fname, field in _fields.items():
            field["required"] = False
        return res

    def _form_get_default_widget_model(self, fname, field):
        """Search via related field needs a simple char widget."""
        res = super()._form_get_default_widget_model(fname, field)
        if fname in self.form_search_domain_rules:
            res = "cms.form.widget.char"
        return res

    def form_process_GET(self, render_values):
        self.form_search(render_values)
        return render_values

    def form_search(self, render_values):
        """Produce search results."""
        search_values = self.form_extract_values()
        if not search_values and not self.form_show_results_no_submit:
            return self.form_search_results
        domain = self.form_search_domain(search_values)
        count = self.form_model.search_count(domain)
        page = render_values.get("extra_args", {}).get("page", 0)
        url = self._form_get_url_for_pager(render_values)
        pager = self._form_results_pager(count=count, page=page, url=url)
        order = self.form_results_orderby or None
        results = self.form_model.search(
            domain,
            limit=self.form_results_per_page,
            offset=pager["offset"],
            order=order,
        )
        self.form_search_results = {
            "results": results,
            "count": count,
            "pager": pager,
        }
        return self.form_search_results

    def _form_get_url_for_pager(self, render_values):
        # default to current path w/out paging
        path = pycompat.to_text(self.request.path)
        url = path.split("/page")[0]
        if self.form_model_name:
            # rely on model's cms search url
            url = getattr(self.form_model, "cms_search_url", None) or url
        # override via controller/request specific value
        url = render_values.get("extra_args", {}).get("pager_url", url)
        return url

    def pager(self, **kw):
        return portal_pager(**kw)

    def _form_results_pager(self, count=None, page=0, url="", url_args=None):
        """Prepare pager for current search."""
        url_args = url_args or self.request.args.to_dict()
        count = count
        return self.pager(
            url=url,
            total=count,
            page=page,
            step=self.form_results_per_page,
            scope=self.form_results_per_page,
            url_args=url_args,
        )

    def form_search_domain(self, search_values):
        """Build search domain."""
        domain = []
        for fname, field in self.form_fields_get().items():
            value = search_values.get(fname)
            if value is None:
                continue
            if fname in self.form_search_fields_multi:
                leaf = (fname, "in", value)
                domain.append(leaf)
                continue
            # TODO: find the way to properly handle this.
            # It would be nice to guess leafs in a clever way.
            operator = "="
            if field["type"] in ("char", "text"):
                # Do not use empty strings
                if not value:
                    continue
                operator = "ilike"
                value = "%{}%".format(value)
            elif field["type"] in ("integer", "float", "many2one"):
                operator = "="
            elif field["type"] in ("one2many", "many2many"):
                if not value:
                    continue
                operator = "in"
            elif field["type"] in ("boolean",):
                value = value == "on" and True
            elif field["type"] in ("date", "datetime"):
                if not value:
                    # searching for an empty string breaks search
                    continue
            if fname in self.form_search_domain_rules:
                rule = self.form_search_domain_rules[fname]
                if callable(rule):
                    fname, operator, value = rule(field, value, search_values)
                else:
                    fname, operator, fmt_value = rule
                    value = fmt_value.format(value) if fmt_value else value
            leaf = (fname, operator, value)
            domain.append(leaf)
        return domain
