# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import base64
import io
import urllib.parse
from contextlib import contextmanager

import mock
from werkzeug.contrib.sessions import SessionStore
from werkzeug.datastructures import FileStorage
from werkzeug.wrappers import Request

from odoo import api, http
from odoo.tests.common import get_db_name


def fake_request(
    form_data=None,
    query_string=None,
    url="/fake/path",
    method="GET",
    content_type=None,
    session=None,
):
    data = urllib.parse.urlencode(form_data or {})
    query_string = query_string or ""
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
    w_req.session = session if session is not None else mock.MagicMock()
    # odoo request
    o_req = http.HttpRequest(w_req)
    o_req.website = mock.MagicMock()
    o_req.csrf_token = mock.MagicMock()
    o_req.httprequest = w_req
    o_req.__testing__ = True
    return o_req


class FakeSessionStore(SessionStore):
    def delete(self, session):
        session.clear()
        del session


session_store = FakeSessionStore(session_class=http.OpenERPSession)


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
    session._fix_lang(session.context)
    for k, v in kw.items():
        if hasattr(session, k):
            setattr(session, k, v)
    session.__testing__ = True
    return session


@contextmanager
def b64_as_stream(b64_content):
    stream = io.BytesIO()
    stream.write(base64.b64decode(b64_content))
    stream.seek(0)
    yield stream
    stream.close()


def fake_file_from_request(input_name, stream, **kw):
    return FileStorage(name=input_name, stream=stream, **kw)
