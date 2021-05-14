# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class FakeSearchPartnerForm(models.AbstractModel):
    """A test model search form."""

    _name = "cms.form.search.res.partner"
    _inherit = "cms.form.search"
    _description = "CMS Form test partner search form"
    _form_model = "res.partner"
    _form_model_fields = (
        "name",
        "country_id",
    )

    def form_search_domain(self, search_values):
        """Force domain to include only test-created records."""
        domain = super().form_search_domain(search_values)
        # we use this attr in tests to limit search results
        # to test records' scope
        include_only_ids = getattr(self, "test_record_ids", [])
        if include_only_ids:
            domain.append(("id", "in", include_only_ids))
        return domain


class FakeSearchPartnerFormMulti(models.AbstractModel):
    """A test model search form w/ multiple values for country."""

    _name = "cms.form.search.res.partner.multicountry"
    _inherit = "cms.form.search.res.partner"
    _description = "CMS Form test partner search multi form"
    _form_search_fields_multi = ("country_id",)

    @property
    def form_widgets(self):
        res = super().form_widgets
        res.update({"country_id": "cms.form.widget.many2one.multi"})
        return res
