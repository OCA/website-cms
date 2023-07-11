# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import json

from odoo import fields, models

from ..fields import Serialized


class Widget(models.AbstractModel):
    _name = "cms.form.widget.mixin"
    _description = "CMS Form widget mixin"

    # use `w_` prefix as a namespace for all widget properties

    id = fields.Id(automatic=True)
    # Special fields
    # TODO: would be better to have python obj fields
    w_form = fields.Binary(store=False)
    w_record = fields.Binary(store=False)
    main_object = fields.Binary(store=False)
    w_field = fields.Binary(store=False)

    w_template = fields.Char(default="")
    w_css_klass = fields.Char(default="")

    w_fname = fields.Char(default="")
    w_field_value = Serialized(default=None)
    w_data = Serialized(default={})
    w_subfields = Serialized(default={})

    def widget_init(
        self,
        form,
        fname,
        field,
        data=None,
        subfields=None,
        template="",
        css_klass="",
        **kw
    ):
        vals = {
            "w_form": form,
            "w_fname": fname,
            "w_field": field,
            "w_field_value": form.form_render_values.get("form_data", {}).get(fname),
            "w_data": data or {},
            "w_subfields": subfields or field.get("subfields", {}),
            "w_template": template,
            "w_css_klass": css_klass,
        }
        widget = self.new(vals)
        return widget

    def render(self):
        return self.env.ref(self.w_template).render({"widget": self})

    @property
    def w_form_model(self):
        return self.w_form.form_model

    @property
    def w_record(self):
        return self.w_form.main_object

    @property
    def w_form_values(self):
        return self.w_form.form_render_values

    def w_load(self, **req_values):
        """Load value for current field in current request."""
        value = self.w_field.get("_default")
        # we could have form-only fields
        if self.w_record and self.w_fname in self.w_record:
            value = self.w_record[self.w_fname] or value
        # maybe a POST request with new values: override item value
        value = req_values.get(self.w_fname, value)
        return value

    def w_extract(self, **req_values):
        """Extract value from form submit."""
        return req_values.get(self.w_fname)

    def w_check_empty_value(self, value, **req_values):
        # `None` values are meant to be ignored as not changed
        return value in (False, "")

    @staticmethod
    def w_ids_from_input(value):
        """Convert list of ids from form input."""
        return [
            int(rec_id.strip())
            for rec_id in value.split(",")
            if rec_id.strip().isdigit()
        ]

    def w_subfields_by_value(self, value="_all"):
        return self.w_subfields.get(value, {})

    def w_data_json(self):
        return json.dumps(self.w_data, sort_keys=True)
