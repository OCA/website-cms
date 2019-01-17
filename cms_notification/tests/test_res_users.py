# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import odoo.tests.common as test_common


class TestUsers(test_common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.msg_model = cls.env['mail.message'].with_context(
            # prevent call to `_notify`, not needed
            message_create_from_mail_mail=True)
        cls.cms_subtype = cls.env['mail.message.subtype'].create({
            'name': 'A CMS type',
            'cms_type': True,
        })
        cls.not_cms_subtype = cls.env['mail.message.subtype'].create({
            'name': 'NOT A CMS type',
        })
        cls.partner = cls.env.ref('base.main_partner')
        cls.demo_user = cls.env.ref('base.user_demo')
        cls.demo_partner = cls.env.ref('base.partner_demo')
        cls.cms_message = cls.msg_model.create({
            'body': 'CMS message',
            'res_id': cls.partner.id,
            'model': 'res.partner',
            'subtype_id': cls.cms_subtype.id,
            'partner_ids': [(6, 0, cls.demo_partner.ids)],
            'needaction_partner_ids': [(6, 0, cls.demo_partner.ids)],
        })
        cls.simple_message = cls.msg_model.create({
            'body': 'NOT CMS message',
            'res_id': cls.partner.id,
            'model': 'res.partner',
            'partner_ids': [(6, 0, cls.demo_partner.ids)],
            'needaction_partner_ids': [(6, 0, cls.demo_partner.ids)],
        })

    def test_has_unread(self):
        self.assertTrue(self.demo_user.has_unread_notif)
        # compued method retrieves msg via search
        # but this change is not reflected so we delete the message
        # which works :S
        # self.cms_message.needaction_partner_ids = False
        self.cms_message.unlink()
        # this guy still have to read `simple_message`
        # but non cms message are not considered
        self.assertFalse(self.demo_user.has_unread_notif)
