# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import json
import os
import unittest

from ..controllers import main
from .common import FormHttpTestCase, FormTestCase
from .utils import fake_request, mock_request

IMPORT = "odoo.addons.cms_form.controllers.main"


class TestControllersAPI(FormTestCase):
    @staticmethod
    def _get_test_models():
        from .fake_models.fake_partner_form import FakePartnerForm
        from .fake_models.fake_search_partner_form import FakeSearchPartnerForm
        from .fake_models.fake_wizard_form import ALL_WIZ_KLASSES

        return ALL_WIZ_KLASSES + [FakePartnerForm, FakeSearchPartnerForm]

    def setUp(self):
        super().setUp()
        self.form_controller = main.CMSFormController()
        self.form_search_controller = main.CMSSearchFormController()
        self.form_wiz_controller = main.CMSWizardFormController()

    def test_get_template(self):
        with mock_request(self.env):
            form = self.form_controller.get_form("res.partner")
            # default
            self.assertEqual(
                self.form_controller.get_template(form),
                "cms_form.portal_form_wrapper",
            )
            # custom on form
            form.form_wrapper_template = "foo.baz"
            self.assertEqual(self.form_controller.get_template(form), "foo.baz")
            self.form_controller.template = None
            form.form_wrapper_template = None
            with self.assertRaises(NotImplementedError):
                self.form_controller.get_template(form)

    def test_get_render_values(self):
        with mock_request(self.env):
            form = self.form_controller.get_form("res.partner")
            # default, no main object
            self.assertEqual(
                self.form_controller.get_render_values(form),
                {
                    "form": form,
                    "main_object": self.env["res.partner"],
                    "controller": self.form_controller,
                },
            )
            # get a main obj
            partner = self.env.ref("base.res_partner_12")
            form = self.form_controller.get_form("res.partner", model_id=partner.id)
            self.assertEqual(
                self.form_controller.get_render_values(form),
                {
                    "form": form,
                    "main_object": partner,
                    "controller": self.form_controller,
                },
            )
            # strip out form fields values (they are held by the form itself)
            self.assertEqual(
                self.form_controller.get_render_values(
                    form, name="John", custom="foo", not_a_form_field=1
                ),
                {
                    "form": form,
                    "main_object": partner,
                    "controller": self.form_controller,
                    "not_a_form_field": 1,
                },
            )

    def test_get_no_form(self):
        with mock_request(self.env):
            # we do not have a specific form for res.groups
            # and cms form is not enabled on partner model
            with self.assertRaises(NotImplementedError):
                self.form_controller.get_form("res.groups")

    def test_get_form_no_model_no_main_object(self):
        with mock_request(self.env):
            form = self.form_controller.get_form(
                None, form_model_key=self.FakePartnerForm._name
            )
            self.assertEqual(form.main_object, self.env[self.FakePartnerForm._name])

    def test_get_default_form(self):
        with mock_request(self.env):
            # we have one for res.partner
            form = self.form_controller.get_form("res.partner")
            self.assertTrue(
                isinstance(form, self.env["cms.form.res.partner"].__class__)
            )
            self.assertEqual(form.form_model_name, "res.partner")
            self.assertEqual(form.form_mode, "create")

    def test_get_specific_form(self):
        with mock_request(self.env):
            # we have a specific form here
            form = self.form_search_controller.get_form("res.partner")
            self.assertTrue(
                isinstance(form, self.env["cms.form.search.res.partner"].__class__)
            )
            self.assertEqual(form.form_model_name, "res.partner")
            self.assertEqual(form.form_mode, "search")

    def test_get_wizard_form(self):
        with mock_request(self.env):
            # we have a specific form here
            form = self.form_wiz_controller.get_form("res.partner")
            self.assertTrue(
                isinstance(form, self.env["cms.form.res.partner"].__class__)
            )
            self.assertEqual(form.form_model_name, "res.partner")
            self.assertEqual(form.form_mode, "create")

    def test_redirect_after_success(self):
        req = fake_request(
            form_data={"name": "John"},
            method="POST",
        )
        with mock_request(self.env, httprequest=req.httprequest):
            partner = self.env.ref("base.res_partner_12")
            response = self.form_controller.make_response(
                "res.partner", model_id=partner.id
            )
            self.assertEqual(response.status_code, 303)
            if "url" in partner:
                # website_partner installed
                self.assertEqual(response.location, partner.url)
            else:
                self.assertEqual(response.location, "/")


@unittest.skipIf(os.getenv("SKIP_HTTP_CASE"), "HTTP case disabled.")
class TestControllersRender(FormHttpTestCase):
    def setUp(self):
        super().setUp()
        self.authenticate("admin", "admin")

    @staticmethod
    def _get_test_models():
        from .fake_models.fake_partner_form import FakePartnerForm
        from .fake_models.fake_search_partner_form import FakeSearchPartnerForm
        from .fake_models.fake_wizard_form import ALL_WIZ_KLASSES

        return ALL_WIZ_KLASSES + [FakePartnerForm, FakeSearchPartnerForm]

    def _check_rendering(self, dom, form_model, model, mode, extra_klass=""):
        """Check default markup for form and form wrapper."""
        # test wrapper klass
        wrapper_node = dom.find_class("cms_form_wrapper")[0]
        expected_attrs = {
            "class": "cms_form_wrapper {form_model} {model} mode_{mode}".format(
                form_model=form_model.replace(".", "_"),
                model=model.replace(".", "_"),
                mode=mode,
            )
            + (" " + extra_klass if extra_klass else "")
        }
        self.assert_match_attrs(wrapper_node.attrib, expected_attrs)
        # test form is there and has correct klass
        form_node = dom.xpath("//form")[0]
        expected_attrs = {
            "enctype": "multipart/form-data",
            "method": "POST",
            "class": "form-horizontal",
        }
        self.assert_match_attrs(form_node.attrib, expected_attrs)

    def _check_route(self, url):
        resp = self.url_open(url, timeout=30)
        self.assertTrue(resp.ok)
        self.assertEqual(resp.status_code, 200)

    def test_default_routes(self):
        self._check_route("/cms/create/res.partner")
        self._check_route("/cms/edit/res.partner/1")
        self._check_route("/cms/search/res.partner")
        self._check_route("/cms/ajax/search/res.partner")

    def test_default_create_rendering(self):
        dom = self.html_get("/cms/create/res.partner")
        self._check_rendering(dom, "cms.form.res.partner", "res.partner", "create")

    def test_default_edit_rendering(self):
        partner = self.env.ref("base.res_partner_1")
        dom = self.html_get("/cms/edit/res.partner/{}".format(partner.id))
        self._check_rendering(dom, "cms.form.res.partner", "res.partner", "edit")

    def _check_wiz_rendering(self, dom, form_model, model, mode, extra_klass=""):
        self._check_rendering(dom, form_model, model, mode, extra_klass=extra_klass)
        # TODO: check more (paging etc)

    def test_default_wiz_rendering(self):
        dom = self.html_get("/cms/wiz/fake.wiz/page/1")
        self._check_wiz_rendering(
            dom,
            "fake.wiz.step1.country",
            "res.country",
            "wizard",
            extra_klass="fake_wiz",
        )
        dom = self.html_get("/cms/wiz/fake.wiz/page/2")
        self._check_wiz_rendering(
            dom,
            "fake.wiz.step2.partner",
            "res.partner",
            "wizard",
            extra_klass="fake_wiz",
        )
        dom = self.html_get("/cms/wiz/fake.wiz/page/3")
        self._check_wiz_rendering(
            dom,
            "fake.wiz.step3.partner",
            "res.partner",
            "wizard",
            extra_klass="fake_wiz",
        )
        # TODO: check more (paging etc)

    def test_render_only_form(self):
        url = self.base_url() + "/cms/render/form/cms.form.res.partner"
        resp = self.url_open(
            url,
            data=json.dumps({"widget_params": {}}),
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        form = resp.json()["result"]["form"]
        dom = self.parse_html(form, fragment=True)
        self.assertTrue(dom.tag == "form")
        data_form = json.loads(dom.attrib["data-form"])
        self.assertEqual(data_form["model"], "res.partner")

    def test_render_only_form_widget(self):
        url = self.base_url() + "/cms/render/form/cms.form.res.partner"
        resp = self.url_open(
            url,
            data=json.dumps({"widget_params": {"custom": {}}}),
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        by_widget = resp.json()["result"]["by_widget"]
        dom = self.parse_html(by_widget["custom"], fragment=True)
        self.assertTrue(dom.tag == "input")
        self.assertEqual(dom.attrib["id"], "custom")
        self.assertEqual(dom.attrib["name"], "custom")
        self.assertEqual(dom.attrib["value"], "oh yeah!")
