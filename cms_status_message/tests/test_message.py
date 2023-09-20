# Copyright 2017 Camptocamp - Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from contextlib import contextmanager
from unittest import mock

from lxml import html

from odoo.tests.common import TransactionCase

from odoo.addons.website.tools import MockRequest

REQ_PATH = "odoo.addons.cms_status_message.models.ir_http.http.request"


class TestMessage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        self.session = {}

    def add_status_message(self, msg, **kw):
        with self.mock_request():
            self.env["ir.http"].add_status_message(msg, **kw)

    def get_status_message(self, **kw):
        with self.mock_request():
            return self.env["ir.http"].get_status_message(**kw)

    @contextmanager
    def mock_request(self):
        request = MockRequest(self.env)
        request.session = self.session
        with mock.patch(REQ_PATH, new=request):
            yield request

    def test_message_add_message(self):
        # we can add one or more messages
        self.add_status_message("well done!")
        self.add_status_message("once again!")
        self.assertTrue("status_message" in self.session)
        msgs = self.get_status_message()
        self.assertEqual(msgs[0]["type"], "info")
        self.assertEqual(msgs[0]["title"], "Info")
        self.assertEqual(msgs[0]["msg"], "well done!")
        self.assertEqual(msgs[1]["type"], "info")
        self.assertEqual(msgs[1]["title"], "Info")
        self.assertEqual(msgs[1]["msg"], "once again!")

    def test_message_add_message_extra_args(self):
        # pass a type
        self.add_status_message("watch out!", kind="warning")
        msg = self.get_status_message()[0]
        self.assertEqual(msg["type"], "warning")
        self.assertEqual(msg["title"], "Warning")
        self.assertEqual(msg["msg"], "watch out!")
        # danger, no title
        self.add_status_message("oh no!", title=None, kind="danger")
        msg = self.get_status_message()[0]
        self.assertEqual(msg["type"], "danger")
        self.assertFalse(msg["title"])
        self.assertEqual(msg["msg"], "oh no!")
        # dismissible
        self.add_status_message("you cannot remove me!", dismissible=False)
        msg = self.get_status_message()[0]
        self.assertEqual(msg["dismissible"], False)
        self.assertEqual(msg["msg"], "you cannot remove me!")

    def _render(self):
        return self.env["ir.qweb"]._render("cms_status_message.status_message", {})

    def _html_get_doc(self, content):
        if not content:
            return None
        return html.document_fromstring(content)

    def test_message_render(self):
        with self.mock_request():
            html_ = self._html_get_doc(self._render())
            self.assertFalse(html_)
            self.add_status_message("oh yeah!")
            html_ = self._html_get_doc(self._render())
            msg = html_.find_class("alert")[0]
            self.assertEqual(msg.attrib["role"], "alert")
            self.assertEqual(msg.attrib["class"], "alert alert-info alert-dismissible")
            self.assertEqual(msg.find_class("msg")[0].text.strip(), "oh yeah!")
            self.assertEqual(msg.find_class("title")[0].text_content().strip(), "Info")

    def test_message_render_types(self):
        with self.mock_request():
            html_ = self._html_get_doc(self._render())
            self.assertFalse(html_)
            expected = [
                ("watch out!", "warning", "Warning"),
                ("oh no!", "danger", "Error"),
                ("foo!", "custom", "Custom"),
            ]
            for msg, kind, title in expected:
                self.add_status_message(msg, kind=kind, title=title)
            html_ = self._html_get_doc(self._render())
            msgs = html_.find_class("alert")

            for i, (msg, kind, title) in enumerate(expected):
                el = msgs[i]
                self.assertEqual(el.attrib["role"], "alert")
                klass = "alert alert-{} alert-dismissible".format(kind)
                self.assertEqual(el.attrib["class"], klass)
                self.assertEqual(el.find_class("msg")[0].text.strip(), msg)
                self.assertEqual(
                    el.find_class("title")[0].text_content().strip(), title
                )

    def test_message_render_no_title(self):
        with self.mock_request():
            html_ = self._html_get_doc(self._render())
            self.assertFalse(html_)
            # no title
            self.add_status_message("no title pls!", title=None)
            html_ = self._html_get_doc(self._render())
            msg = html_.find_class("alert")[0]
            self.assertEqual(msg.find_class("msg")[0].text.strip(), "no title pls!")
            self.assertFalse(msg.find_class("title"))

    def test_message_render_dismissible(self):
        with self.mock_request():
            html_ = self._html_get_doc(self._render())
            self.assertFalse(html_)
            # no title
            self.add_status_message("I stay here forever!", dismissible=0)
            html_ = self._html_get_doc(self._render())
            msg = html_.find_class("alert")[0]
            self.assertFalse("alert-dismissible" in msg.attrib["class"])
