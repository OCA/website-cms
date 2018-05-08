# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


import werkzeug
from lxml import html
import mock
import json
from contextlib import contextmanager

from odoo.tests.common import HttpCase
from ..controllers import main
from .fake_models import FakePublishModel


IMPORT = 'odoo.addons.cms_delete_content.controllers.main'


def setup_test_model(env, model_cls):
    """Pass a test model class and initialize it.
    Courtesy of SBidoul from https://github.com/OCA/mis-builder :)
    """
    model_cls._build_model(env.registry, env.cr)
    env.registry.setup_models(env.cr)
    env.registry.init_models(
        env.cr, [model_cls._name],
        dict(env.context, update_custom_fields=True)
    )


def teardown_test_model(env, model_cls):
    """Pass a test model class and deinitialize it.
    Courtesy of SBidoul from https://github.com/OCA/mis-builder :)
    """
    if not getattr(model_cls, '_teardown_no_delete', False):
        del env.registry.models[model_cls._name]
    env.registry.setup_models(env.cr)


class TestDelete(HttpCase):

    TEST_MODELS_KLASSES = [
        FakePublishModel,
    ]

    at_install = False
    post_install = True

    def setUp(self):
        super(TestDelete, self).setUp()
        for kls in self.TEST_MODELS_KLASSES:
            setup_test_model(self.env, kls)
        self.authenticate('admin', 'admin')
        self.delete_controller = main.DeleteController()
        self.record = self.env[FakePublishModel._name].create({'name': 'New'})

    def tearDown(self):
        # HttpCase has no ENV on setUpClass
        for kls in self.TEST_MODELS_KLASSES:
            teardown_test_model(self.env, kls)
        super(TestDelete, self).tearDown()

    @contextmanager
    def mock_request(self, impot_to_mock, mock_get=True):
        """Mocks some stuff like request."""
        with mock.patch('%s.request' % impot_to_mock) as request:
            request.session = self.session
            request.env = self.env
            # request.httprequest = faked.httprequest
            if mock_get:
                request.get_main_object = lambda x, y: self.record
            request.website_enabled = False
            yield {
                'request': request,
            }

    def to_xml_node(self, html_):
        return html.fragments_fromstring(html_)[0]

    def test_get_main_object(self):
        with self.mock_request(IMPORT, mock_get=False):
            with self.assertRaises(werkzeug.exceptions.NotFound):
                # obj does not exists
                self.delete_controller.get_main_object(
                    FakePublishModel._name, 9999999)
            self.assertEqual(
                self.delete_controller.get_main_object(
                    FakePublishModel._name, self.record.id),
                self.record
            )

    def test_delete_confirm(self):
        with self.mock_request(IMPORT):
            resp = self.url_open(self.record.cms_delete_confirm_url).read()
            node = self.to_xml_node(resp)
            self.assertEqual(
                node.find_class('modal-title')[0].text_content().strip(),
                'Are you sure you want to delete this item?'
            )

    def test_delete(self):
        with self.mock_request(IMPORT):
            resp = self.delete_controller.handle_delete(
                FakePublishModel._name, self.record.id)
            self.assertEqual(
                json.loads(resp),
                {"redirect": "",
                 "message": "%s deleted." % FakePublishModel._description}
            )
            self.assertFalse(self.record.exists())
