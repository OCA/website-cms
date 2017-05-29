# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import openerp.tests.common as test_common


class TestContent(test_common.TransactionCase):

    @property
    def model(self):
        return self.env['testmodel.content']

    def test_default_fields(self):
        item = self.model.create({
            'name': 'Foo',
            'description': 'Just testing this fake model',
            'body': '<p><strong>Yeah!</strong> HTML here!</p>',
        })
        self.assertEqual(item.name, 'Foo')
        self.assertEqual(item.description, 'Just testing this fake model')
        self.assertEqual(item.body, '<p><strong>Yeah!</strong> HTML here!</p>')

    def test_toggle_published(self):
        item = self.model.create({'name': 'Publish me pls!'})
        self.assertFalse(item.website_published)
        self.assertFalse(item.published_uid)
        self.assertFalse(item.published_date)
        item.toggle_published()
        self.assertTrue(item.website_published)
        self.assertTrue(item.published_uid)
        self.assertTrue(item.published_date)

    def test_url(self):
        item = self.model.create({'name': 'Find me here'})
        self.assertEqual(
            item.website_url,
            u'/contents/find-me-here-{}'.format(item.id))
