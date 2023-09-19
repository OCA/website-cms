# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


import werkzeug

from odoo import fields, models
from odoo.tools.image import image_data_uri


class BinaryWidget(models.AbstractModel):
    _name = "cms.form.widget.binary.mixin"
    _inherit = "cms.form.widget.mixin"
    _description = "CMS Form binary widget"

    def w_extract(self, **req_values):
        value = super().w_extract(**req_values)
        return self.form_to_binary(value, **req_values)

    def form_to_binary(self, value, **req_values):
        if self.html_fname not in req_values:
            return None
        _value = False
        keepcheck_flag_key = self.html_fname + "_keepcheck"
        keepcheck_flag = req_values.get(keepcheck_flag_key)
        # If no keepcheck flag is given the file or img is always replaced
        if keepcheck_flag_key in req_values and keepcheck_flag == "yes":
            # no flag or flag marked as "keep current value"
            # prevent discarding image
            req_values.pop(self.html_fname, None)
            req_values.pop(keepcheck_flag_key, None)
            return None
        if value:
            _value = value
            # TODO: move this to image widget
            if isinstance(value, str):
                if value.startswith("data:"):
                    # like 'data:image/jpeg;base64,jRyRuUm2VP...
                    _value = value.split(",")[-1]
            elif isinstance(value, dict):
                _value = value.get("value")
        return _value

    def w_check_empty_value(self, value, **req_values):
        if isinstance(value, werkzeug.datastructures.FileStorage):
            has_value = bool(value.filename)
            keep_flag = req_values.get(self.w_fname + "_keepcheck")
            if not has_value and keep_flag == "yes":
                # no value, but we want to preserve existing one
                return False
            # file field w/ no content
            # TODO: this is not working sometime...
            # return not bool(value.content_length)
            return not has_value
        return super().w_check_empty_value(value, **req_values)


class ImageWidget(models.AbstractModel):
    _name = "cms.form.widget.image"
    _inherit = "cms.form.widget.binary.mixin"
    _description = "CMS Form image widget"

    w_template = fields.Char(default="cms_form.field_widget_image")

    def w_load(self, **req_values):
        value = super().w_load(**req_values)
        # TODO: can we get a dict here? Likely only when loading from request
        if isinstance(value, dict) and value.get("mimetype", "").startswith("image/"):
            val = (
                value["value"].encode()
                if isinstance(value["value"], str)
                else value["value"]
            )
            value["value"] = image_data_uri(val)
        elif isinstance(value, (str, bytes)):
            bvalue = value
            if isinstance(value, str):
                bvalue = value.encode()
            else:
                value = value.decode()
            if value.startswith("data:"):
                raw_value = value.split(",")[-1]
            else:
                raw_value = value
                value = image_data_uri(bvalue)
            mimetype = value.split(";")[0].replace("data:", "")
            value = {
                "value": value,
                "raw_value": raw_value,
                "mimetype": mimetype,
                "content_type": mimetype,
                "content_lenght": len(raw_value),
            }
        return value


class FileWidget(models.AbstractModel):
    _name = "cms.form.widget.binary"
    _inherit = "cms.form.widget.binary.mixin"
    _description = "CMS Form file widget"

    w_template = fields.Char(default="cms_form.field_widget_file")
