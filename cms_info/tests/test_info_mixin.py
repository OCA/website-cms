# Copyright 2018 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import mock
from odoo_test_helper import FakeModelLoader

import odoo.tests.common as test_common
from odoo import exceptions


class TestInfoMixin(test_common.SavepointCase):

    post_install = True
    at_install = False

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from .fake_models import FakeModel

        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        cls.loader.update_registry((FakeModel,))
        cls.model = cls.env[FakeModel._name]
        cls.record = cls.model.create({"name": "Foo"})
        user_model = cls.env["res.users"].with_context(
            tracking_disable=True, no_reset_password=True
        )
        cls.user1 = user_model.create(
            {
                "name": "User 1",
                "login": "user1",
                "email": "user1@email.com",
                "groups_id": [(6, 0, [cls.env.ref("base.group_portal").id])],
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def test_create_url(self):
        self.assertEqual(self.record.cms_create_url, "/cms/create/fake.model")

    def test_search_url(self):
        self.assertEqual(self.record.cms_search_url, "/cms/search/fake.model")

    def test_edit_url(self):
        self.assertEqual(
            self.record.cms_edit_url, "/cms/edit/fake.model/%s" % self.record.id,
        )

    def test_delete_url(self):
        self.assertEqual(
            self.record.cms_delete_url, "/cms/delete/fake.model/%s" % self.record.id,
        )
        self.assertEqual(
            self.record.cms_delete_confirm_url,
            "/cms/delete/fake.model/%s/confirm" % self.record.id,
        )
        self.assertEqual(
            self.record.cms_after_delete_url, "/",
        )

    def test_is_owner(self):
        self.assertTrue(self.record.cms_is_owner())
        self.assertFalse(self.record.with_user(self.user1).cms_is_owner())

    # No special ACL nor record rule.
    # Rely on the fact that access rights checks are called in the right way
    # and depending on their result we get proper cms info.
    def test_can_create(self):
        path_rights = "odoo.models.Model.check_access_rights"
        with mock.patch(path_rights) as mocked:
            mocked.return_value = False
            self.assertFalse(self.model.with_user(self.user1).cms_can_create())
            mocked.assert_called_with("create", raise_exception=False)
            mocked.return_value = True
            self.assertTrue(self.model.with_user(self.user1).cms_can_create())
            mocked.assert_called_with("create", raise_exception=False)

    def _test_can(self, record, mode, handler):
        path_rights = "odoo.models.Model.check_access_rights"
        path_rule = "odoo.models.Model.check_access_rule"
        with mock.patch(path_rights) as mocked_rights, mock.patch(
            path_rule
        ) as mocked_rule:
            # test false
            mocked_rights.side_effect = exceptions.AccessError("BAM!")
            mocked_rule.side_effect = exceptions.AccessError("BAM!")
            self.assertFalse(handler())
            mocked_rights.assert_called_with(mode)
            # failed on ACL check, no call here
            mocked_rule.assert_not_called()

        with mock.patch(path_rights) as mocked_rights, mock.patch(
            path_rule
        ) as mocked_rule:
            # test true only rights
            mocked_rights.return_value = True
            mocked_rule.side_effect = exceptions.AccessError("BAM!")
            self.assertFalse(handler())
            mocked_rights.assert_called_with(mode)
            mocked_rule.assert_called_with(mode)

        with mock.patch(path_rights) as mocked_rights, mock.patch(
            path_rule
        ) as mocked_rule:
            # test true
            mocked_rights.return_value = True
            mocked_rule.return_value = True
            self.assertTrue(handler())
            mocked_rights.assert_called_with(mode)
            mocked_rule.assert_called_with(mode)

    def test_can_edit(self):
        record = self.record.with_user(self.user1)
        self._test_can(record, "write", record.cms_can_edit)

    def test_can_delete(self):
        record = self.record.with_user(self.user1)
        self._test_can(record, "unlink", record.cms_can_delete)

    def test_can_publish(self):
        record = self.record.with_user(self.user1)
        self._test_can(record, "write", record.cms_can_publish)

    def test_info_on_record(self):
        info = self.record.cms_info()
        keys = (
            "is_owner",
            "can_edit",
            "can_create",
            "can_publish",
            "can_delete",
            "create_url",
            "edit_url",
            "delete_url",
        )
        self.assertEqual(sorted(keys), sorted(info.keys()))

    def test_info_on_model(self):
        info = self.record.browse().cms_info()
        keys = (
            "is_owner",
            "can_edit",
            "can_create",
            "can_publish",
            "can_delete",
            "create_url",
            "edit_url",
            "delete_url",
        )
        self.assertEqual(sorted(keys), sorted(info.keys()))
