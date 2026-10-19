# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import tagged

from .common import FormHttpTestCase


@tagged("post_install", "-at_install")
class TestFormTour(FormHttpTestCase):
    """Frontend behaviour of the form, driven by JS tours."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tag = cls.env["res.partner.category"].create({"name": "Tour tag"})

    def setUp(self):
        super().setUp()
        self.authenticate("admin", "admin")

    @staticmethod
    def _get_test_models():
        from .fake_models.fake_tour_form import FakeTourPartner, FakeTourPartnerForm

        return [FakeTourPartner, FakeTourPartnerForm]

    def test_tour_create_form(self):
        self.start_tour(
            "/cms/create/fake.tour.partner",
            "cms_form_create_form",
            login="admin",
        )
