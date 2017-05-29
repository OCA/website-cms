# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import openerp.tests.common as test_common
from .base import BaseSecurityTestCase


class TestSecurity(BaseSecurityTestCase, test_common.TransactionCase):

    @property
    def model(self):
        return self.env['testmodel.secured']
