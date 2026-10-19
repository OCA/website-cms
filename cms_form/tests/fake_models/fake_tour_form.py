# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models

from odoo.addons.cms_form.models.fields import Serialized  # pylint: disable=W8150


class FakeTourPartner(models.TransientModel):
    """Record used by the frontend tours (transient: no ACL setup needed)."""

    _name = "fake.tour.partner"
    _description = "CMS Form tour fake record"

    name = fields.Char()
    kind = fields.Selection(
        [("person", "Person"), ("company", "Company")], default="person"
    )
    company_name = fields.Char()
    birthdate = fields.Date()
    tag_ids = fields.Many2many("res.partner.category")
    notes = fields.Text()


class FakeTourPartnerForm(models.AbstractModel):
    """Form exercising master/slave, date and many2many widgets."""

    _name = "cms.form.fake.tour.partner"
    _inherit = "cms.form"
    _description = "CMS Form tour form"

    form_model_name = fields.Char(default="fake.tour.partner")
    form_model_fields = Serialized(
        default=("name", "kind", "company_name", "birthdate", "tag_ids", "notes")
    )
    form_required_fields = Serialized(default=("name",))

    def _form_master_slave_info(self):
        return {
            "kind": {
                "hide": {"company_name": ("person",)},
                "show": {"company_name": ("company",)},
            }
        }
