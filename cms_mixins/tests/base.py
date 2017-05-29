# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
# import openerp.tests.common as test_common
from openerp import exceptions


class BaseSecurityTestCase(object):
    """Base klass to test your model basic permissions.

    You can reuse this to test all your models' access.
    Just provide a proper `model` property.
    """

    @property
    def model(self):
        raise NotImplementedError()

    def setUp(self):
        super(BaseSecurityTestCase, self).setUp()
        user_model = self.env['res.users'].with_context(no_reset_password=1)
        self.user1 = user_model.create({
            'name': 'User 1 (test ref)',
            'login': 'testref_user1',
            'email': 'testref_user1@email.com',
            # make sure to have only portal group
            'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
        })
        self.user2 = user_model.create({
            'name': 'User2',
            'login': 'testref_user2',
            'email': 'testref_user2@email.com',
            # make sure to have only portal group
            'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
        })
        self.group_public = self.env.ref('base.group_public')
        self.user_public = self.env['res.users'].with_context(
            {'no_reset_password': True,
             'mail_create_nosubscribe': True}
        ).create({
            'name': 'Public User',
            'login': 'publicuser',
            'email': 'publicuser@example.com',
            'groups_id': [(6, 0, [self.group_public.id])]}
        )

    def test_perm_create(self):
        ref = self.model.sudo(self.user1.id).create({'name': 'Foo'})
        self.assertTrue(self.model.browse(ref.id))

    def test_perm_write(self):
        ref = self.model.sudo(self.user1.id).create({'name': 'Foo'})
        ref.name = 'Baz'
        self.assertEqual(ref.name, 'Baz')

    def test_perm_write_only_owner(self):
        ref = self.model.sudo(self.user1.id).create({'name': 'Foo'})
        with self.assertRaises(exceptions.AccessError):
            ref.sudo(self.user2.id).name = 'cannot do this!'
        ref = self.model.sudo(self.user2.id).create({'name': 'Foo 2'})
        with self.assertRaises(exceptions.AccessError):
            ref.sudo(self.user1.id).name = 'cannot do this!'
        with self.assertRaises(exceptions.AccessError):
            ref.sudo(self.user_public.id).name = 'cannot do this!'

    def test_delete(self):
        ref = self.model.sudo(self.user1.id).create({'name': 'Foo'})
        ref_id = ref.id
        ref.unlink()
        self.assertFalse(self.model.browse(ref_id).exists())

        # test delete w/ attachment field
        # Reported issue https://github.com/odoo/odoo/issues/15311
        # Overridden unlink method in ProjectReference
        ref = self.model.sudo(self.user1.id).create({
            'name': 'Foo',
            'image': 'fake image here!'.encode('base64')
        })
        ref_id = ref.id
        ref.unlink()
        self.assertFalse(self.model.browse(ref_id).exists())

    def test_delete_only_owner(self):
        ref = self.model.sudo(self.user1.id).create({'name': 'Foo'})
        with self.assertRaises(exceptions.AccessError):
            ref.sudo(self.user2.id).unlink()
        with self.assertRaises(exceptions.AccessError):
            ref.sudo(self.user_public.id).unlink()

    def test_published(self):
        ref = self.model.sudo(self.user1.id).create({'name': 'Foo'})
        self.assertFalse(ref.website_published)
        # admin
        self.assertTrue(ref.read())
        # owner
        self.assertTrue(ref.sudo(self.user1.id).read())
        # public user
        with self.assertRaises(exceptions.AccessError):
            ref.sudo(self.user_public.id).read()
        # another portal user
        with self.assertRaises(exceptions.AccessError):
            ref.sudo(self.user2.id).read()
        # publish it!
        ref.website_published = True
        # now public user can see it
        self.assertTrue(ref.sudo(self.user_public.id).read())
        # and other portal user too
        self.assertTrue(ref.sudo(self.user2.id).read())

    def test_perm_read_group_ids(self):
        ref = self.model.sudo(self.user1.id).create({'name': 'Foo'})
        with self.assertRaises(exceptions.AccessError):
            ref.sudo(self.user2.id).name
        # sharing group
        group = self.env['res.groups'].create({'name': 'View Team'})
        self.user2.write({'groups_id': [(4, group.id)]})
        ref.write({'read_group_ids': [(4, group.id)]})
        # now user2 can read
        self.assertTrue(ref.sudo(self.user2.id).name)
        # public user still cannot access
        with self.assertRaises(exceptions.AccessError):
            ref.sudo(self.user_public.id).name

    def test_perm_write_group_ids(self):
        ref = self.model.sudo(self.user1.id).create({'name': 'Foo'})
        with self.assertRaises(exceptions.AccessError):
            ref.sudo(self.user2.id).name = 'New name here!'
        # sharing group
        group = self.env['res.groups'].create({'name': 'Write Team'})
        self.user2.write({'groups_id': [(4, group.id)]})
        ref.write({'write_group_ids': [(4, group.id)]})
        # now user2 can write
        ref.sudo(self.user2.id).name = 'New name here!'
        self.assertEqual(ref.name, 'New name here!')
        # public user still cannot access
        with self.assertRaises(exceptions.AccessError):
            ref.sudo(self.user_public.id).name = 'not me!'
