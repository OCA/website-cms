# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import mock

from odoo import exceptions

from .common import FormTestCase


class TestFormPermCheck(FormTestCase):
    @staticmethod
    def _get_test_models():
        from .fake_models.fake_partner_form import FakePartnerForm
        from .fake_models.fake_pub_model_form import FakePubModel
        from .fake_models.fake_pub_model_form import FakePubModelForm
        from .fake_models.fake_nonpub_model_form import FakeNonPubModel
        from .fake_models.fake_nonpub_model_form import FakeNonPubModelForm

        return (
            FakeNonPubModel,
            FakeNonPubModelForm,
            FakePartnerForm,
            FakePubModel,
            FakePubModelForm,
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.record = cls.env[cls.FakePubModel._name].create({"name": "Foo"})

    @classmethod
    def tearDownClass(cls):
        cls.record.unlink()
        super().tearDownClass()

    mixin_path = "odoo.addons.cms_info.models.cms_mixin.CMSInfoMixin"

    def test_form_check_permission_can_create(self):
        form = self.get_form(self.FakePubModelForm._name, main_object=None)
        with mock.patch(self.mixin_path + ".cms_can_create") as patched:
            patched.return_value = True
            self.assertTrue(form.form_check_permission())
            patched.assert_called()

    def test_form_check_permission_cannot_create(self):
        form = self.get_form(self.FakePubModelForm._name, main_object=None)
        with mock.patch(self.mixin_path + ".cms_can_create") as patched:
            patched.return_value = False
            try:
                form.form_check_permission()
            except exceptions.AccessError as err:
                patched.assert_called()
                msg = (
                    "You are not allowed to create any record " "for the model `%s`."
                ) % self.FakePubModel._name
                self.assertEqual(err.name, msg)

    def test_form_check_permission_can_edit(self):
        form = self.get_form(self.FakePubModelForm._name, main_object=self.record)
        with mock.patch(self.mixin_path + ".cms_can_edit") as patched:
            patched.return_value = True
            self.assertTrue(form.form_check_permission())
            patched.assert_called()

    def test_form_check_permission_cannot_edit(self):
        form = self.get_form(self.FakePubModelForm._name, main_object=self.record)
        with mock.patch(self.mixin_path + ".cms_can_edit") as patched:
            patched.return_value = False
            try:
                form.form_check_permission()
            except exceptions.AccessError as err:
                patched.assert_called()
                msg = ("You cannot edit this record. Model: %s, ID: %d.") % (
                    self.record._name,
                    self.record.id,
                )
                self.assertEqual(err.name, msg)

    def test_form_check_permission_no_ws_mixin_can_create(self):
        form = self.get_form(self.FakeNonPubModelForm._name, main_object=None)
        self.assertTrue(form.form_check_permission())

    def test_form_check_permission_no_ws_mixin_can_edit(self):
        rec = self.env[self.FakeNonPubModel._name].create({"name": "Foo"})
        form = self.get_form(self.FakeNonPubModelForm._name, main_object=rec)
        self.assertTrue(form.form_check_permission())

    def test_form_check_permission_no_record_no_model_can_edit_create(self):
        form = self.get_form(self.FakePartnerForm._name, main_object=None)
        form._form_model = None
        self.assertTrue(form._can_edit())
        self.assertTrue(form._can_create())

    def test_form_check_permission_form_cannot_edit(self):
        form = self.get_form(self.FakePartnerForm._name, main_object=self.record)
        with mock.patch.object(type(self.record), "check_access_rights") as patched:
            patched.side_effect = exceptions.AccessError("boom")
            with self.assertRaises(exceptions.AccessError):
                form._can_edit()
            self.assertFalse(form._can_edit(raise_exception=False))
