# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import openerp.tests.common as test_common
from openerp import exceptions


class TestParent(test_common.TransactionCase):

    @property
    def model(self):
        return self.env['testmodel.parent']

    def test_parent_children(self):
        parent = self.model.create({
            'name': 'Parent',
        })
        child1 = self.model.create({
            'name': 'Child 1',
            'parent_id': parent.id,
        })
        child2 = self.model.create({
            'name': 'Child 2',
            'parent_id': parent.id,
        })
        subchild1 = self.model.create({
            'name': 'Sub Child 1',
            'parent_id': child1.id,
        })
        self.assertIn(child1, parent.children_ids)
        self.assertIn(child2, parent.children_ids)
        self.assertEqual(child1.parent_id, parent)
        self.assertEqual(child2.parent_id, parent)
        self.assertIn(subchild1, child1.children_ids)
        self.assertEqual(subchild1.parent_id, child1)

    def test_avoid_recursive(self):
        parent = self.model.create({
            'name': 'Parent',
        })
        with self.assertRaises(exceptions.ValidationError):
            parent.parent_id = parent

    def test_open_children(self):
        parent = self.model.create({
            'name': 'Parent',
        })
        act = parent.open_children()
        self.assertEqual(act['context']['default_parent_id'], parent.id)
        for k, v in parent._open_children_context().iteritems():
            self.assertEqual(act['context'][k], v)
        self.assertEqual(act['domain'], [('parent_id', '=', parent.id)])

    def _create_hierarchy(self, parent=None):
        item = parent or self.model.create({
            'name': 'Parent',
        })
        all_items = [item, ]
        for x in xrange(1, 6):
            item = self.model.create({
                'name': str(x),
                'parent_id': item.id
            })
            all_items.append(item)
        return all_items

    def test_hierarchy(self):
        all_items = self._create_hierarchy()
        # last
        last = all_items[-1]
        hierarchy = last.hierarchy()
        self.assertEqual(len(all_items) - 1, len(hierarchy))
        for item in all_items[:-1]:
            self.assertIn(item, hierarchy)
        # last -1
        last = all_items[-2]
        hierarchy = last.hierarchy()
        self.assertEqual(len(all_items) - 2, len(hierarchy))
        for item in all_items[:-2]:
            self.assertIn(item, hierarchy)

    def test_path(self):
        all_items = self._create_hierarchy()
        path = all_items[-1].path()
        self.assertEqual(path, u'/Parent/1/2/3/4')

    def test_name_get(self):
        all_items = self._create_hierarchy()
        last = all_items[-1]
        self.assertEqual(last.name_get()[0][1], last.name)
        self.assertEqual(
            last.with_context(include_path=1).name_get()[0][1],
            u'/Parent/1/2/3/4 > {}'.format(last.name)
        )

    def test_listing(self):
        all_items1 = self._create_hierarchy()
        all_items2 = self._create_hierarchy()
        root = self.model.create({
            'name': 'Root',
        })
        all_items1[0].parent_id = root
        all_items2[0].parent_id = root

        # get direct children
        self.assertEqual(len(root.get_listing()), 2)
        # get all descendants
        self.assertEqual(
            len(root.get_listing(direct=False)),
            len(all_items1) + len(all_items2))
        # get all descendants filtered
        listing = root.get_listing(
            direct=False, extra_domain=[('name', '=', '1')])
        self.assertEqual(len(listing), 2)
