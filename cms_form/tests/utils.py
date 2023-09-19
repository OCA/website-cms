# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import base64
import io
import urllib.parse
from contextlib import contextmanager
from unittest import mock

from werkzeug.datastructures import FileStorage
from werkzeug.wrappers import Request

from odoo import api, http
from odoo.tests.common import get_db_name
from odoo.tools import DotDict
from odoo.tools._vendor.sessions import SessionStore

from odoo.addons.website.tools import MockRequest


def fake_request(
    form_data=None,
    query_string=None,
    url="/fake/path",
    method="GET",
    content_type=None,
    session=None,
):
    data = urllib.parse.urlencode(form_data or {})
    content_type = content_type or "application/x-www-form-urlencoded"
    # werkzeug request
    w_req = Request.from_values(
        url,
        query_string=query_string,
        content_length=len(data),
        input_stream=io.StringIO(data),
        content_type=content_type,
        method=method,
    )
    # odoo request
    o_req = http.Request(w_req)
    o_req.csrf_token = mock.MagicMock()
    o_req.httprequest = w_req
    o_req.session = session if session is not None else mock.MagicMock()
    o_req.__testing__ = True
    return o_req


@contextmanager
def mock_request(
    env,
    request=None,
    httprequest=None,
    extra_headers=None,
    request_attrs=None,
    httprequest_attrs=None,
    **kw
):
    # TODO: refactor this ctx mngr from website to:
    # - make it independent
    # - use real request and session as per fake_request above
    with MockRequest(env, **kw) as mocked_request:
        if httprequest:
            if isinstance(httprequest, dict):
                httprequest = DotDict(httprequest)
            mocked_request.httprequest = httprequest
        headers = {}
        headers.update(extra_headers or {})
        mocked_request.httprequest.headers = headers
        request_attrs = request_attrs or {}
        for k, v in request_attrs.items():
            setattr(mocked_request, k, v)
        httprequest_attrs = httprequest_attrs or {}
        for k in ("args", "form", "files", "_cms_form_files_processed"):
            if k not in httprequest_attrs:
                httprequest_attrs[k] = {}
        for k, v in httprequest_attrs.items():
            setattr(mocked_request.httprequest, k, v)
        mocked_request.make_response = lambda data, **kw: data
        mocked_request.registry._init_modules = set()
        mocked_request.session.touch = lambda: True
        yield mocked_request


class FakeSessionStore(SessionStore):
    def delete(self, session):
        session.clear()
        del session


session_store = FakeSessionStore(session_class=http.Session)


def fake_session(env, **kw):
    db = get_db_name()
    env = api.Environment(env.cr, env.uid, {})
    session = session_store.new()
    session.db = db
    session.uid = env.uid
    session.login = env.user.login
    session.password = ""
    session.context = dict(env.context)
    session.context["uid"] = env.uid
    for k, v in kw.items():
        if hasattr(session, k):
            setattr(session, k, v)
    session.__testing__ = True
    return session


@contextmanager
def file_as_stream(content):
    stream = io.BytesIO()
    stream.write(content)
    stream.seek(0)
    yield stream
    stream.close()


@contextmanager
def b64_as_stream(b64_content):
    with file_as_stream(base64.b64decode(b64_content)) as stream:
        yield stream


def fake_file_from_request(input_name, stream, **kw):
    return FileStorage(name=input_name, stream=stream, **kw)
