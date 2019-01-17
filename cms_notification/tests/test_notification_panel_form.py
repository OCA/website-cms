# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.cms_form.tests.common import FormTestCase
from odoo.addons.cms_form.tests.utils import fake_request
from .fake_models import FakeNotificationPanel


def add_xmlid(env, record, xmlid, noupdate=False):
    """ Add a XMLID on an existing record """
    try:
        ref_id, __, __ = env['ir.model.data'].xmlid_lookup(xmlid)
    except ValueError:
        pass  # does not exist, we'll create a new one
    else:
        return env['ir.model.data'].browse(ref_id)
    if '.' in xmlid:
        module, name = xmlid.split('.')
    else:
        module = ''
        name = xmlid
    return env['ir.model.data'].create({
        'name': name,
        'module': module,
        'model': record._name,
        'res_id': record.id,
        'noupdate': noupdate,
    })


class CMSNotificationCase(FormTestCase):

    TEST_MODELS_KLASSES = [FakeNotificationPanel, ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # from base cms_form test case
        cls._setup_models()
        cls._setup_records()

    @classmethod
    def tearDownClass(cls):
        cls._teardown_models()
        super().tearDownClass()

    @classmethod
    def _setup_records(cls):
        user_model = cls.env['res.users'].with_context(
            no_reset_password=True, tracking_disable=True)
        cls.user1 = user_model.create({
            'name': 'Marty McFly',
            'login': 'marty',
            'email': 'marty@email.com',
        })
        cls.subtype_model = cls.env['mail.message.subtype']
        cls.subtype1 = cls.subtype_model.create(
            {'name': 'Back to the future I'})
        add_xmlid(cls.env, cls.subtype1, 'cms_notification.test_subtype1')
        cls.subtype2 = cls.subtype_model.create(
            {'name': 'Back to the future II'})
        add_xmlid(cls.env, cls.subtype2, 'cms_notification.test_subtype2')
        cls.subtype3 = cls.subtype_model.create(
            {'name': 'Back to the future III'})
        add_xmlid(cls.env, cls.subtype3, 'cms_notification.test_subtype3')

    def _assert_values(self, expected, values):
        for k, v in expected.items():
            self.assertEqual(values[k], v)

    def test_form_next_url(self):
        form = self.get_form('cms.notification.panel.form')
        self.assertEqual(form.form_next_url(), '/my/settings/notifications')

    def test_form_next_url_redirect(self):
        req = fake_request(query_string='redirect=/foo')
        form = self.get_form('cms.notification.panel.form', req=req)
        self.assertEqual(form.form_next_url(), '/foo')

    def test_form_defaults(self):
        form = self.get_form(
            'cms.notification.panel.form',
            main_object=self.user1,
            sudo_uid=self.user1.id)
        defaults = form.form_load_defaults()
        expected = dict(
            # not specific record for disabling: all ON
            enable_1=True,
            enable_2=True,
            enable_3=True,
        )
        self._assert_values(expected, defaults)

        self.user1._notify_enable_subtype(self.subtype1)
        self.user1._notify_enable_subtype(self.subtype2)
        self.user1._notify_disable_subtype(self.subtype3)
        defaults = form.form_load_defaults()
        expected = dict(
            enable_1=True,
            enable_2=True,
            enable_3=False,
        )
        self._assert_values(expected, defaults)

    def test_form_updates(self):
        data = {
            'enable_1': 'on',
            'enable_2': '',
            'enable_3': 'on',
        }
        req = fake_request(form_data=data, method='POST')
        form = self.get_form(
            'cms.notification.panel.form', req=req, main_object=self.user1)
        form.form_process()
        self.assertIn(self.subtype1, self.user1.enabled_notify_subtype_ids)
        self.assertIn(self.subtype2, self.user1.disabled_notify_subtype_ids)
        self.assertIn(self.subtype3, self.user1.enabled_notify_subtype_ids)
