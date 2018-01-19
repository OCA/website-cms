# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from io import StringIO
from werkzeug.wrappers import Request
import mock
import urllib.parse

from odoo import http


def fake_request(form_data=None, query_string=None,
                 method='GET', content_type=None):
    data = urllib.parse.urlencode(form_data or {})
    query_string = query_string or ''
    content_type = content_type or 'application/x-www-form-urlencoded'
    # werkzeug request
    w_req = Request.from_values(
        query_string=query_string,
        content_length=len(data),
        input_stream=StringIO(data),
        content_type=content_type,
        method=method)
    w_req.session = mock.MagicMock()
    # odoo request
    o_req = http.HttpRequest(w_req)
    o_req.website = mock.MagicMock()
    o_req.csrf_token = mock.MagicMock()
    o_req.httprequest = w_req
    o_req.__testing__ = True
    return o_req


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
