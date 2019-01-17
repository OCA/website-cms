# Copyright 2018 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import odoo.tests.common as test_common


class TestMailMessage(test_common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.msg_model = cls.env['mail.message'].with_context(
            # prevent call to `_notify`, not needed
            message_create_from_mail_mail=True)
        cls.partner = cls.env.ref('base.main_partner')
        cls.demo_user = cls.env.ref('base.user_demo')
        cls.demo_partner = cls.env.ref('base.partner_demo')
        cls.message = cls.msg_model.create({
            'body': 'My Body',
            'res_id': cls.partner.id,
            'model': 'res.partner',
            'partner_ids': [(6, 0, cls.demo_partner.ids)],
            'needaction_partner_ids': [(6, 0, cls.demo_partner.ids)],
        })

    def test_ref_selection(self):
        sel = self.message._selection_ref_item_id()
        # we can select all models
        for model in self.env["ir.model"].search([]):
            self.assertIn((model.model, model.name), sel)

    def test_ref_model(self):
        self.assertEqual(
            self.message.ref_model_id,
            self.env['ir.model']._get('res.partner')
        )

    def test_ref_item(self):
        self.assertEqual(
            self.message.ref_item_id,
            self.env.ref('base.main_partner')
        )

    def test_is_unread(self):
        self.assertTrue(self.message.sudo(self.demo_user).is_unread())

    def test_is_read(self):
        self.message.needaction_partner_ids = False
        self.assertTrue(self.message.sudo(self.demo_user).is_read())
