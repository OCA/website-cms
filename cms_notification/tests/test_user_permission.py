# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import odoo.tests.common as test_common
from odoo import exceptions
from odoo.tools import mute_logger


class TestPermission(test_common.TransactionCase):

    def setUp(self):
        super(TestPermission, self).setUp()
        user_model = self.env['res.users'].with_context(no_reset_password=1)
        self.user1 = user_model.create({
            'name': 'User 1',
            'login': 'user1',
            'email': 'user1@email.com',
            # make sure to have only portal group
            'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
        })
        self.user2 = user_model.create({
            'name': 'User 2',
            'login': 'user2',
            'email': 'user2@email.com',
            # make sure to have only portal group
            'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
        })

    def test_user_can_edit_own_record(self):
        self.user1.sudo(self.user1).write({'name': 'Foo'})
        self.assertEqual(self.user1.name, 'Foo')

    @mute_logger('odoo.models')
    def test_user_cannot_edit_other_users(self):
        with self.assertRaises(exceptions.AccessError):
            self.user1.sudo(self.user2).write({'name': 'Foo'})
        with self.assertRaises(exceptions.AccessError):
            self.user2.sudo(self.user1).write({'name': 'Foo'})
