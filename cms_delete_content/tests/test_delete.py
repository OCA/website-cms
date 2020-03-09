# Copyright 2017-2018 Camptocamp - Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


import werkzeug
from lxml import html
import mock
import json
from contextlib import contextmanager

from odoo.addons.cms_form.tests.common import FormHttpTestCase
from ..controllers import main
from .fake_models import FakePublishModel


IMPORT = 'odoo.addons.cms_delete_content.controllers.main'


class TestDelete(FormHttpTestCase):

    TEST_MODELS_KLASSES = [
        FakePublishModel,
    ]

    at_install = False
    post_install = True

    def setUp(self):
        super().setUp()
        self.authenticate('admin', 'admin')
        self.delete_controller = main.DeleteController()
        self.record = self.env[FakePublishModel._name].create({'name': 'New'})

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
            response = self.url_open(
                self.record.cms_delete_confirm_url, timeout=30)
            content = response.content
            node = self.to_xml_node(content)
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
