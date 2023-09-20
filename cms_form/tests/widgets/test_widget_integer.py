# Copyright 2019 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from .common import TestWidgetCase, fake_field, fake_form


class TestWidgetInteger(TestWidgetCase):

    # TODO: test extraction and conversion to proper field value
    # on EVERY widget and not just rely on the marshallers.
    # Of course we have to switch to `html_fname` approach as hidden widget.
    # This implies that we test w/ a full request too.

    def setUp(self):
        super().setUp()
        form = fake_form(self.env, an_int_field=10)
        self.w_name, self.w_field = fake_field("an_int_field", type="integer")
        self.widget = self.get_widget(
            self.w_name,
            self.w_field,
            form=form,
            widget_model="cms.form.widget.integer",
        )

    def test_widget_integer_input(self):
        expected_attrs = {
            "type": "number",
            "id": "an_int_field",
            "name": "an_int_field",
            "placeholder": "An int field...",
            "value": "10",
            "class": "form-control ",
        }
        self._test_widget_attributes(self.widget, "input", expected_attrs)

    def test_widget_integer_input_required(self):
        self.widget.w_field["required"] = True
        expected_attrs = {
            "type": "number",
            "id": "an_int_field",
            "name": "an_int_field",
            "placeholder": "An int field...",
            "value": "10",
            "class": "form-control ",
            "required": "1",
        }
        self._test_widget_attributes(self.widget, "input", expected_attrs)

    def test_widget_integer_input_extract(self):
        self.assertEqual(self.widget.w_extract(an_int_field="1"), 1)
        self.assertEqual(self.widget.w_extract(an_int_field="4"), 4)
        self.assertEqual(self.widget.w_extract(an_int_field="2.0"), None)
        self.assertEqual(self.widget.w_extract(an_int_field=""), None)
