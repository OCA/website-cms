# -*- coding: utf-8 -*-

from openerp.tests import common

from openerp.addons.cms_mixin.tests.base import BaseSecurityTestCase


class TestSecurity(BaseSecurityTestCase, common.TransactionCase):

    @property
    def model(self):
        return self.env['cms.page']
