# Copyright 2018 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import odoo.tests.common as test_common
from .fake_models import FakeModel


class TestInfoMixin(test_common.SavepointCase):

    post_install = True
    at_install = False

    TEST_MODELS_KLASSES = [FakeModel, ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for kls in cls.TEST_MODELS_KLASSES:
            kls._test_setup_model(cls.env)
        cls.record = cls.env[FakeModel._name].create({'name': 'Foo'})
        user_model = cls.env['res.users'].with_context(
            tracking_disable=True, no_reset_password=True)
        cls.user1 = user_model.create({
            'name': 'User 1',
            'login': 'user1',
            'email': 'user1@email.com',
            'groups_id': [(6, 0, [cls.env.ref('base.group_portal').id])]
        })

    @classmethod
    def tearDownClass(cls):
        for kls in cls.TEST_MODELS_KLASSES:
            kls._test_teardown_model(cls.env)
        super().tearDownClass()

    def test_create_url(self):
        self.assertEqual(self.record.cms_create_url, '/cms/create/fake.model')

    def test_search_url(self):
        self.assertEqual(self.record.cms_search_url, '/cms/search/fake.model')

    def test_edit_url(self):
        self.assertEqual(
            self.record.cms_edit_url,
            '/cms/edit/fake.model/%s' % self.record.id)

    def test_is_owner(self):
        self.record._test_create_ACL(
            group_id=self.env.ref('base.group_portal').id
        )
        self.assertTrue(self.record.cms_is_owner())
        self.assertFalse(self.record.sudo(self.user1).cms_is_owner())

    def test_can_create(self):
        self.assertTrue(self.env[FakeModel._name].cms_can_create())
        self.assertFalse(
            self.env[FakeModel._name].sudo(self.user1).cms_can_create()
        )

    def test_can_edit(self):
        self.record._test_create_ACL(
            group_id=self.env.ref('base.group_portal').id,
            perm_write=False,
        )
        self.assertTrue(self.record.cms_can_edit())
        self.assertFalse(self.record.sudo(self.user1).cms_can_edit())

    def test_can_publish(self):
        # this permission by default is just a proxy to "can edit"
        self.record._test_create_ACL(
            group_id=self.env.ref('base.group_portal').id,
            perm_write=False,
        )
        self.assertTrue(self.record.cms_can_publish())
        self.assertFalse(self.record.sudo(self.user1).cms_can_publish())

    def test_can_delete(self):
        self.record._test_create_ACL(
            group_id=self.env.ref('base.group_portal').id,
            perm_write=False,
            perm_unlink=False,
        )
        self.assertTrue(self.record.cms_can_delete())
        self.assertFalse(self.record.sudo(self.user1).cms_can_delete())

    def test_info_on_record(self):
        info = self.record.cms_info()
        keys = (
            'is_owner',
            'can_edit',
            'can_create',
            'can_publish',
            'can_delete',
            'create_url',
            'edit_url',
            'delete_url',
        )
        self.assertEqual(sorted(keys), sorted(info.keys()))

    def test_info_on_model(self):
        info = self.record.browse().cms_info()
        keys = (
            'is_owner',
            'can_edit',
            'can_create',
            'can_publish',
            'can_delete',
            'create_url',
            'edit_url',
            'delete_url',
        )
        self.assertEqual(sorted(keys), sorted(info.keys()))
