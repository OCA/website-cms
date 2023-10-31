# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models

from odoo.addons.cms_form.models.fields import Serialized  # pylint: disable=W8150

TEST_RECORD_IDS = []


class FakeSearchPartnerForm(models.AbstractModel):
    """A test model search form."""

    _name = "cms.form.search.res.partner"
    _inherit = "cms.form.search"
    _description = "CMS Form test partner search form"

    form_model_name = fields.Char(default="res.partner")
    form_model_fields = Serialized(default=("name", "country_id"))

    def form_search_domain(self, search_values):
        """Force domain to include only test-created records."""
        domain = super().form_search_domain(search_values)
        # we use this attr in tests to limit search results
        # to test records' scope
        include_only_ids = self._get_test_record_ids()
        if include_only_ids:
            domain.append(("id", "in", include_only_ids))
        return domain

    @classmethod
    def _get_test_record_ids(cls):
        global TEST_RECORD_IDS
        return TEST_RECORD_IDS

    @classmethod
    def _set_test_record_ids(cls, ids):
        global TEST_RECORD_IDS
        TEST_RECORD_IDS = ids


class FakeSearchPartnerFormMulti(models.AbstractModel):
    """A test model search form w/ multiple values for country."""

    _name = "cms.form.search.res.partner.multicountry"
    _inherit = "cms.form.search.res.partner"
    _description = "CMS Form test partner search multi form"

    form_search_fields_multi = Serialized(default=("country_id",))
    country_id = fields.Many2one(
        comodel_name="res.country",
        form_widget={"model": "cms.form.widget.many2one.multi"},
    )
