# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


import werkzeug
from lxml import html
import mock
import json
from contextlib import contextmanager

from openerp.tests.common import HttpCase
from ..controllers import main

IMPORT = 'openerp.addons.cms_delete_content.controllers.main'


class TestDelete(HttpCase):

    at_install = False
    post_install = True

    def setUp(self):
        super(TestDelete, self).setUp()
        self.authenticate('admin', 'admin')
        self.delete_controller = main.DeleteController()
        self.partner = self.env['res.partner'].create({'name': 'New'})

    @contextmanager
    def mock_request(self, impot_to_mock, mock_get=True):
        """Mocks some stuff like request."""
        with mock.patch('%s.request' % impot_to_mock) as request:
            request.session = self.session
            request.env = self.env
            # request.httprequest = faked.httprequest
            if mock_get:
                request.get_main_object = lambda x, y: self.partner
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
                    'res.partner', 9999999)
            self.assertEqual(
                self.delete_controller.get_main_object(
                    'res.partner', self.partner.id),
                self.partner
            )

    def test_delete_confirm(self):
        with self.mock_request(IMPORT):
            resp = self.url_open(self.partner.cms_delete_confirm_url).read()
            node = self.to_xml_node(resp)
            self.assertEqual(
                node.find_class('modal-title')[0].text_content().strip(),
                'Are you sure you want to delete this item?'
            )

    def test_delete(self):
        with self.mock_request(IMPORT):
            resp = self.delete_controller.handle_delete(
                'res.partner', self.partner.id)
            self.assertEqual(
                json.loads(resp),
                {"redirect": "", "message": "Partner deleted."}
            )
            self.assertFalse(self.partner.exists())
