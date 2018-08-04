# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.cms_form.tests.common import FormTestCase


class TestNotificationListing(FormTestCase):

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
            'needaction_partner_ids': [(6, 0, cls.demo_partner.ids)],
        })

    def test_form_domain(self):
        form = self.get_form(
            'cms.notification.listing',
            sudo_uid=self.demo_user.id)
        expected = [
            ('partner_ids', 'in', [self.demo_partner.id, ]),
            ('subtype_id.cms_type', '=', True),
        ]
        domain = form.form_search_domain({})
        self.assertListEqual(domain, expected)

    def test_form_domain2(self):
        form = self.get_form(
            'cms.notification.listing',
            sudo_uid=self.demo_user.id)
        expected = [
            ('subtype_id', '=', 10),
            ('partner_ids', 'in', [self.demo_partner.id, ]),
            ('subtype_id.cms_type', '=', True),
        ]
        domain = form.form_search_domain({'subtype_id': 10})
        self.assertListEqual(domain, expected)

    # TODO: test search result
