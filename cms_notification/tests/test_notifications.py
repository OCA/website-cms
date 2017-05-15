# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp.tests.common import TransactionCase
from openerp.addons.cms_form.tests.common import fake_request


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


class CMSNotificationCase(TransactionCase):

    at_install = False
    post_install = True

    def setUp(self):
        super(CMSNotificationCase, self).setUp()
        self.partner_model = self.env['res.partner']
        self.subtype_model = self.env['mail.message.subtype']

        self.partner1 = self.partner_model.with_context(
            tracking_disable=1).create({'name': 'Marty McFly'})
        self.subtype1 = self.subtype_model.create(
            {'name': 'Back to the future I'})
        add_xmlid(self.env, self.subtype1, 'cms_notification.test_subtype1')
        self.subtype2 = self.subtype_model.create(
            {'name': 'Back to the future II'})
        add_xmlid(self.env, self.subtype2, 'cms_notification.test_subtype2')
        self.subtype3 = self.subtype_model.create(
            {'name': 'Back to the future III'})
        add_xmlid(self.env, self.subtype3, 'cms_notification.test_subtype3')
        self.form_model_key = 'cms.notification.panel.form'

    def get_form(self, req=None, **kw):
        request = req or fake_request()
        return self.env[self.form_model_key].form_init(request, **kw)

    def _assert_values(self, expected, values):
        for k, v in expected.iteritems():
            self.assertEqual(values[k], v)

    def test_form_defaults(self):
        form = self.get_form(main_object=self.partner1)
        defaults = form.form_load_defaults()
        expected = dict(
            # not specific record for disabling: all ON
            enable_1=True,
            enable_2=True,
            enable_3=True,
        )
        self._assert_values(expected, defaults)

        self.partner1._notify_enable_subtype(self.subtype1)
        self.partner1._notify_enable_subtype(self.subtype2)
        self.partner1._notify_disable_subtype(self.subtype3)
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
            req=req, main_object=self.partner1)
        form.form_process()
        self.assertIn(self.subtype1, self.partner1.enabled_notify_subtype_ids)
        self.assertIn(self.subtype2, self.partner1.disabled_notify_subtype_ids)
        self.assertIn(self.subtype3, self.partner1.enabled_notify_subtype_ids)
