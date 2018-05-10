# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from lxml import html
from odoo.tests.common import SavepointCase, HttpCase
from .utils import (
    fake_request, fake_session, session_store,
    setup_test_model, teardown_test_model
)


class FormTestMixin(object):

    at_install = False
    post_install = True

    def get_form(self, form_model, req=None, session=None,
                 ctx=None, sudo_uid=None, **kw):
        """Retrieve and initialize a form.

        :param form_model: model dotted name
        :param req: a fake request. Default to base fake request
        :param kw: extra arguments to init the form
        """
        model = self.env[form_model]
        if sudo_uid:
            model = model.sudo(sudo_uid)
        if ctx:
            model = model.with_context(**ctx)

        session = session if session is not None else fake_session(self.env)
        request = req or fake_request(session=session)
        return model.form_init(request, **kw)

    # override this in your test case to inject new models on the fly
    TEST_MODELS_KLASSES = []

    @classmethod
    def _setup_models(cls):
        """Setup new fake models for testing."""
        for kls in cls.TEST_MODELS_KLASSES:
            setup_test_model(cls.env, kls)

    @classmethod
    def _teardown_models(cls):
        """Wipe fake models once tests have finished."""
        for kls in cls.TEST_MODELS_KLASSES:
            teardown_test_model(cls.env, kls)


class FormRenderMixin(FormTestMixin):

    def to_xml_node(self, html_):
        return html.fragments_fromstring(html_)

    def find_input_name(self, node, name):
        return node.xpath(
            '(//input|//select|//textarea)[@name="{}"]'.format(name))

    def assert_match_attrs(self, value, expected):
        for k, v in expected.iteritems():
            self.assertEqual(value[k].strip(), v.strip())

    def assert_match_inputs(self, node, expected):
        for name in expected:
            self.assertEqual(len(self.find_input_name(node, name)), 1)


class FormTestCase(SavepointCase, FormTestMixin):
    """Base class for transaction cases."""


class FormSessionTestCase(SavepointCase, FormTestMixin):
    """Base class for transaction cases."""

    def setUp(self):
        super(FormSessionTestCase, self).setUp()
        self.session = fake_session(self.env)

    def tearDown(self):
        # self.session.clear()
        session_store.delete(self.session)
        super(FormSessionTestCase, self).tearDown()


class FormRenderTestCase(SavepointCase, FormRenderMixin):
    """Base class for http cases."""


class FormHttpTestCase(HttpCase, FormRenderMixin):

    def setUp(self):
        # HttpCase has no ENV on setUpClass
        super(FormHttpTestCase, self).setUp()
        for kls in self.TEST_MODELS_KLASSES:
            setup_test_model(self.env, kls)

    def tearDown(self):
        # HttpCase has no ENV on setUpClass
        for kls in self.TEST_MODELS_KLASSES:
            teardown_test_model(self.env, kls)
        super(FormHttpTestCase, self).tearDown()

    def html_get(self, url):
        resp = self.url_open(url, timeout=30)
        return html.document_fromstring(resp.read())
