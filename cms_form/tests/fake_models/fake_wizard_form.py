# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class FakeWiz(models.AbstractModel):
    """A wizard form."""

    FAKE_STORAGE = {}

    _name = "fake.wiz"
    _inherit = "cms.form.wizard"
    _description = "CMS Form test wizard form"
    _wiz_name = _name

    def form_check_permission(self, raise_exception=True):
        # no need for this
        pass

    @property
    def _wiz_storage(self):
        return self.FAKE_STORAGE

    def wiz_configure_steps(self):
        return {
            1: {"form_model": "fake.wiz.step1.country"},
            2: {"form_model": "fake.wiz.step2.partner"},
            3: {"form_model": "fake.wiz.step3.partner"},
        }


class FakeWizStep1Country(models.AbstractModel):

    _name = "fake.wiz.step1.country"
    _inherit = "fake.wiz"
    _description = "CMS Form test wizard form step 1"
    _form_model = "res.country"
    _form_model_fields = ("name",)


class FakeWizStep2Partner(models.AbstractModel):

    _name = "fake.wiz.step2.partner"
    _inherit = "fake.wiz"
    _description = "CMS Form test wizard form step 2"
    _form_model = "res.partner"
    _form_model_fields = (
        "name",
        "to_be_stored",
    )
    _wiz_step_stored_fields = ("to_be_stored",)

    to_be_stored = fields.Char()


class FakeWizStep3Partner(models.AbstractModel):

    _name = "fake.wiz.step3.partner"
    _inherit = "fake.wiz"
    _description = "CMS Form test wizard form step 3"
    _form_model = "res.partner"
    _form_model_fields = ("name",)


ALL_WIZ_KLASSES = [
    FakeWiz,
    FakeWizStep1Country,
    FakeWizStep2Partner,
    FakeWizStep3Partner,
]
