# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from lxml import html

from odoo.orm.model_classes import add_to_registry
from odoo.tests.common import HttpCase, TransactionCase, tagged

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


class FakeModelMixin:
    """Mixin to setup fake models just for testing."""

    @staticmethod
    def _get_test_models():
        return ()

    @staticmethod
    def _setup_models(class_or_instance):
        """Setup new fake models for testing.

        Odoo 19 registers test models natively, no odoo_test_helper needed.
        """
        if hasattr(class_or_instance, "_fake_model_names"):
            # Especially for HttpCase: try to setup models only once
            return
        test_models = class_or_instance._get_test_models()
        class_or_instance._fake_model_names = []
        if not test_models:
            return
        registry = class_or_instance.registry
        for klass in test_models:
            add_to_registry(registry, klass)
            class_or_instance._fake_model_names.append(klass._name)
            # Make them available on the test class
            setattr(class_or_instance, klass.__name__, klass)
        names = class_or_instance._fake_model_names
        registry._setup_models__(class_or_instance.env.cr, names)
        registry.init_models(class_or_instance.env.cr, names, {"models_to_check": True})

    @staticmethod
    def _teardown_models(class_or_instance):
        """Wipe fake models once tests have finished."""
        registry = class_or_instance.registry
        for name in getattr(class_or_instance, "_fake_model_names", []):
            registry.__delitem__(name)
        class_or_instance._fake_model_names = []


class HTMLRenderMixin:
    """Mixin with helpers to test HTML rendering."""

    def to_xml_node(self, html_):
        return html.fragments_fromstring(html_)

    def find_input_name(self, node, name):
        return node.xpath(f'(//input|//select|//textarea)[@name="{name}"]')

    def assert_match_attrs(self, value, expected):
        for k, v in expected.items():
            self.assertEqual(value[k].strip(), v.strip())

    def assert_match_inputs(self, node, expected):
        for name in expected:
            self.assertEqual(len(self.find_input_name(node, name)), 1)


@tagged("post_install", "-at_install")
class FormTestCase(TransactionCase, FakeModelMixin):
    """Form test cases."""

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


@tagged("post_install", "-at_install")
class FormHttpTestCase(HttpCase, FakeModelMixin, HTMLRenderMixin):
    """Form test cases where you test HTML rendering and HTTP requests."""

    # FIXME: use setupClass
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
        return self.parse_html(resp.content)

    def parse_html(self, content, fragment=False):
        parser = html.document_fromstring
        if fragment:
            parser = html.fragment_fromstring
        return parser(content)

    def get_form(self, form_model, **kw):
        return get_form(self.env, form_model, **kw)
