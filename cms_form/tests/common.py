# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from lxml import html
from odoo_test_helper import FakeModelLoader

from odoo.tests.common import HttpCase, SavepointCase

from .utils import fake_request, fake_session, session_store


def get_form(env, form_model, req=None, session=None, ctx=None, sudo_uid=None, **kw):
    """Retrieve and initialize a form.

    :param form_model: model dotted name
    :param req: a fake request. Default to base fake request
    :param session: a fake session. Default to base fake session
    :param ctx: extra context keys
    :param sudo_uid: init form w/ another user uid
    :param kw: extra arguments to init the form
    """
    model = env[form_model]
    if sudo_uid:
        model = model.with_user(sudo_uid)
    if ctx:
        model = model.with_context(**ctx)

    session = session if session is not None else fake_session(env)
    request = req or fake_request(session=session)
    return model.form_init(request, **kw)


class FakeModelMixin(object):
    """Mixin to setup fake models just for testing."""

    @staticmethod
    def _get_test_models():
        return ()

    @staticmethod
    def _setup_models(class_or_instance):
        """Setup new fake models for testing."""
        if hasattr(class_or_instance, "loader"):
            # Especially for HttpCase: try to setup models only once
            return
        class_or_instance.loader = FakeModelLoader(
            class_or_instance.env, class_or_instance.__module__
        )
        class_or_instance.loader.backup_registry()
        test_models = class_or_instance._get_test_models()
        if test_models:
            class_or_instance.loader.update_registry(test_models)
            for klass in test_models:
                # Make them available on the test class
                setattr(class_or_instance, klass.__name__, klass)

    @staticmethod
    def _teardown_models(class_or_instance):
        """Wipe fake models once tests have finished."""
        if hasattr(class_or_instance, "loader"):
            class_or_instance.loader.restore_registry()


class HTMLRenderMixin(object):
    """Mixin with helpers to test HTML rendering."""

    def to_xml_node(self, html_):
        return html.fragments_fromstring(html_)

    def find_input_name(self, node, name):
        return node.xpath('(//input|//select|//textarea)[@name="{}"]'.format(name))

    def assert_match_attrs(self, value, expected):
        for k, v in expected.items():
            self.assertEqual(value[k].strip(), v.strip())

    def assert_match_inputs(self, node, expected):
        for name in expected:
            self.assertEqual(len(self.find_input_name(node, name)), 1)


class FormTestCase(SavepointCase, FakeModelMixin):
    """Form test cases."""

    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_models(cls)

    @classmethod
    def tearDownClass(cls):
        cls._teardown_models(cls)
        super().tearDownClass()

    def get_form(self, form_model, **kw):
        return get_form(self.env, form_model, **kw)


class FormSessionTestCase(FormTestCase):
    """Form test cases where you deal w/ a session."""

    def setUp(self):
        super().setUp()
        self.session = fake_session(self.env)

    def tearDown(self):
        session_store.delete(self.session)
        super().tearDown()


class FormRenderTestCase(FormTestCase, HTMLRenderMixin):
    """Form test cases where you test HTML rendering."""


class FormHttpTestCase(HttpCase, FakeModelMixin, HTMLRenderMixin):
    """Form test cases where you test HTML rendering and HTTP requests."""

    def setUp(self):
        # HttpCase has no ENV on setUpClass we have to setup fake models here
        super().setUp()
        self._setup_models(self)

    def tearDown(self):
        # HttpCase has no ENV on setUpClass
        self._teardown_models(self)
        super().tearDown()

    def html_get(self, url):
        resp = self.url_open(url, timeout=30)
        return html.document_fromstring(resp.content)

    def get_form(self, form_model, **kw):
        return get_form(self.env, form_model, **kw)
