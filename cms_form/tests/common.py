# -*- coding: utf-8 -*-
# Copyright 2016 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.tests.common import HttpCase
from openerp import http
from werkzeug.wrappers import Request
import mock
from cStringIO import StringIO
import urllib
from lxml import html


def fake_request(form_data=None, query_string=None,
                 method='GET', content_type=None):
    data = urllib.urlencode(form_data or {})
    query_string = query_string or ''
    content_type = content_type or 'application/x-www-form-urlencoded'
    req = Request.from_values(
        query_string=query_string,
        content_length=len(data),
        input_stream=StringIO(data),
        content_type=content_type,
        method=method)
    req.session = mock.MagicMock()
    o_req = http.HttpRequest(req)
    o_req.website = mock.MagicMock()
    o_req.csrf_token = mock.MagicMock()
    return o_req


class FormTestMixin(object):

    at_install = False
    post_install = True

    def get_form(self, form_model, req=None, **kw):
        request = req or fake_request()
        return self.env[form_model].form_init(request, **kw)


class FormRenderMixin(FormTestMixin):

    def to_xml_node(self, html_):
        return html.fragments_fromstring(html_)

    def find_input_name(self, node, name):
        return node.xpath('//input[@name="{}"]'.format(name))

    def assert_match_attrs(self, value, expected):
        for k, v in expected.iteritems():
            self.assertEqual(value[k].strip(), v.strip())

    def assert_match_inputs(self, node, expected):
        for name in expected:
            self.assertEqual(len(self.find_input_name(node, name)), 1)


class FormTestCase(TransactionCase, FormTestMixin):
    """Base class for transaction cases."""


class FormRenderTestCase(TransactionCase, FormRenderMixin):
    """Base class for http cases."""


class FormHttpTestCase(HttpCase, FormRenderMixin):

    def html_get_doc(self, url):
        return html.document_fromstring(self.url_open(url, timeout=30).read())