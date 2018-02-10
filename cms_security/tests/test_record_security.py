# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

import odoo.tests.common as test_common
from .base import BasePermissionTestCase
from .fake_models import FakeSecuredModel
from .fake_models import setup_test_model
from .fake_models import teardown_test_model


class TestSecurity(BasePermissionTestCase, test_common.SavepointCase):
    """All tests come from `BasePermissionTestCase`."""

    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        setup_test_model(cls.env, FakeSecuredModel)

    @classmethod
    def tearDownClass(cls):
        teardown_test_model(cls.env, FakeSecuredModel)
        super().tearDownClass()

    @property
    def model(self):
        return self.env['fakemodel.secured']
