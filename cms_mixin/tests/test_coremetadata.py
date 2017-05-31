# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import openerp.tests.common as test_common
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from mock import patch


def dt_fromstring(dt):
    return datetime.strptime(dt, DEFAULT_SERVER_DATETIME_FORMAT)


@test_common.at_install(False)
@test_common.post_install(True)
class TestCoremetadata(test_common.TransactionCase):

    def setUp(self):
        super(TestCoremetadata, self).setUp()
        mod = 'openerp.addons.cms_mixin.models.coremetadata.fields.Datetime'
        self.patcher = patch(mod)
        self.mock_datetime = self.patcher.start()

    @property
    def model(self):
        return self.env['testmodel.coremetadata']

    def _freeze_date(self, dt_string):
        dt = dt_fromstring(dt_string)
        self.mock_datetime.now.return_value = dt

    def test_published_create(self):
        now = '2017-05-30 00:00:00'
        self._freeze_date(now)

        item = self.model.create({'name': 'Foo', 'website_published': True})
        self.assertTrue(item.website_published)
        self.assertEqual(item.published_uid.id, self.env.user.id)
        self.assertEqual(item.published_date, now)

    def test_published_write(self):
        item = self.model.create({'name': 'Foo'})
        self.assertFalse(item.website_published)
        self.assertFalse(item.published_uid)

        now = '2017-05-30 01:00:00'
        self._freeze_date(now)
        item.website_published = True
        self.assertEqual(item.published_uid.id, self.env.user.id)
        self.assertEqual(item.published_date, now)
