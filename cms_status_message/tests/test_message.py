# Copyright 2017-2018 Camptocamp - Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from contextlib import contextmanager

import mock
from lxml import html

from odoo.tests.common import HttpCase

_logger = logging.getLogger(__name__)


IMPORT = "odoo.addons.cms_status_message.models.website"


class HTMLCase(HttpCase):
    def setUp(self):
        super().setUp()
        self.authenticate("admin", "admin")
        self.website = self.env["website"].browse(1)

    @contextmanager
    def mock_assets(self):
        """Mocks some stuff like request."""
        with mock.patch("%s.request" % IMPORT) as request:
            request.session = self.session
            yield {
                "request": request,
            }

    def html_get_doc(self, url):
        response = self.url_open(url, timeout=30)
        return html.document_fromstring(response.content)

    def test_message_add_message(self):
        # we can add one or more messages
        self.website.add_status_message("well done!", session=self.session)
        self.website.add_status_message("once again!", session=self.session)
        self.assertTrue("status_message" in self.session)
        msgs = self.website.get_status_message(session=self.session)
        self.assertEqual(msgs[0]["type"], "info")
        self.assertEqual(msgs[0]["title"], "Info")
        self.assertEqual(msgs[0]["msg"], "well done!")
        self.assertEqual(msgs[1]["type"], "info")
        self.assertEqual(msgs[1]["title"], "Info")
        self.assertEqual(msgs[1]["msg"], "once again!")

    def test_message_add_message_extra_args(self):
        # pass a type
        self.website.add_status_message(
            "watch out!", type_="warning", session=self.session
        )
        msg = self.website.get_status_message(session=self.session)[0]
        self.assertEqual(msg["type"], "warning")
        self.assertEqual(msg["title"], "Warning")
        self.assertEqual(msg["msg"], "watch out!")
        # danger, no title
        self.website.add_status_message(
            "oh no!", title=None, type_="danger", session=self.session
        )
        msg = self.website.get_status_message(session=self.session)[0]
        self.assertEqual(msg["type"], "danger")
        self.assertFalse(msg["title"])
        self.assertEqual(msg["msg"], "oh no!")
        # dismissible
        self.website.add_status_message(
            "you cannot remove me!", dismissible=False, session=self.session
        )
        msg = self.website.get_status_message(session=self.session)[0]
        self.assertEqual(msg["dismissible"], False)
        self.assertEqual(msg["msg"], "you cannot remove me!")

    def test_message_render(self):
        with self.mock_assets() as assets:
            session = assets["request"].session
            html_ = self.html_get_doc("/")
            self.assertFalse(html_.find_class("alert"))
            self.website.add_status_message("oh yeah!", session=session)
            html_ = self.html_get_doc("/")
            msg = html_.find_class("alert")[0]
            self.assertEqual(msg.attrib["role"], "alert")
            self.assertEqual(msg.attrib["class"], "alert alert-info alert-dismissible")
            self.assertEqual(msg.find_class("msg")[0].text.strip(), "oh yeah!")
            self.assertEqual(msg.find_class("title")[0].text_content().strip(), "Info")

    def test_message_render_types(self):
        with self.mock_assets() as assets:
            session = assets["request"].session
            html_ = self.html_get_doc("/")
            self.assertFalse(html_.find_class("alert"))

            expected = [
                ("watch out!", "warning", "Warning"),
                ("oh no!", "danger", "Error"),
                ("foo!", "custom", "Custom"),
            ]
            for msg, type_, title in expected:
                self.website.add_status_message(
                    msg, session=session, type_=type_, title=title
                )
            html_ = self.html_get_doc("/")
            msgs = html_.find_class("alert")

            for i, (msg, type_, title) in enumerate(expected):
                el = msgs[i]
                self.assertEqual(el.attrib["role"], "alert")
                klass = "alert alert-{} alert-dismissible".format(type_)
                self.assertEqual(el.attrib["class"], klass)
                self.assertEqual(el.find_class("msg")[0].text.strip(), msg)
                self.assertEqual(
                    el.find_class("title")[0].text_content().strip(), title
                )

    def test_message_render_no_title(self):
        with self.mock_assets() as assets:
            session = assets["request"].session
            html_ = self.html_get_doc("/")
            self.assertFalse(html_.find_class("alert"))
            # no title
            self.website.add_status_message(
                "no title pls!", session=session, title=None
            )
            html_ = self.html_get_doc("/")
            msg = html_.find_class("alert")[0]
            self.assertEqual(msg.find_class("msg")[0].text.strip(), "no title pls!")
            self.assertFalse(msg.find_class("title"))

    def test_message_render_dismissible(self):
        with self.mock_assets() as assets:
            session = assets["request"].session
            html_ = self.html_get_doc("/")
            self.assertFalse(html_.find_class("alert"))
            # no title
            self.website.add_status_message(
                "I stay here forever!", session=session, dismissible=0
            )
            html_ = self.html_get_doc("/")
            msg = html_.find_class("alert")[0]
            self.assertFalse("alert-dismissible" in msg.attrib["class"])
