# -*- coding: utf-8 -*-
# Copyright 2016 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp import http
from werkzeug.wrappers import Request
import mock
from cStringIO import StringIO
import urllib


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


class FormTestCase(TransactionCase):

    at_install = False
    post_install = True

    def get_form(self, form_model, req=None, **kw):
        request = req or fake_request()
        return self.env[form_model].form_init(request, **kw)
