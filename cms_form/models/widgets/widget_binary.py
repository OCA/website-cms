# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import werkzeug
import base64

from odoo.tools import pycompat
from odoo.tools.mimetypes import guess_mimetype
from odoo import models


class BinaryWidget(models.AbstractModel):
    _name = 'cms.form.widget.binary.mixin'
    _inherit = 'cms.form.widget.mixin'

    def w_load(self, **req_values):
        value = super().w_load(**req_values)
        return self.binary_to_form(value, **req_values)

    def binary_to_form(self, value, **req_values):
        _value = {
            # 'value': '',
            # 'raw_value': '',
            # 'mimetype': '',
        }
        from_request = False
        if value:
            if isinstance(value, werkzeug.datastructures.FileStorage):
                from_request = True
                byte_content = value.read()
                value = base64.b64encode(byte_content)
                if not isinstance(value, pycompat.text_type):
                    value = pycompat.to_text(value)
            else:
                if not isinstance(
                        value, pycompat.text_type):  # pragma: no cover
                    value = value.encode()
                byte_content = base64.b64decode(value)
            mimetype = guess_mimetype(byte_content)
            _value = {
                'value': value,
                'raw_value': value,
                'mimetype': mimetype,
                'from_request': from_request,
            }
            if mimetype.startswith('image/'):
                _value['value'] = 'data:{};base64,{}'.format(mimetype, value)
        return _value

    def w_extract(self, **req_values):
        value = super().w_extract(**req_values)
        return self.form_to_binary(value, **req_values)

    def form_to_binary(self, value, **req_values):
        if self.w_fname not in req_values:
            return None
        _value = False
        keepcheck_flag = req_values.get(self.w_fname + '_keepcheck')
        if not keepcheck_flag or keepcheck_flag == 'yes':
            # no flag or flag marked as "keep current value"
            # prevent discarding image
            req_values.pop(self.w_fname, None)
            req_values.pop(self.w_fname + '_keepcheck', None)
            return None
        if value:
            if hasattr(value, 'read'):
                file_content = value.read()
                _value = base64.b64encode(file_content)
                if not isinstance(value, pycompat.text_type):
                    _value = pycompat.to_text(_value)
            else:
                # like 'data:image/jpeg;base64,jRyRuUm2VP...
                _value = value.split(',')[-1]
        return _value

    def w_check_empty_value(self, value, **req_values):
        if isinstance(value, werkzeug.datastructures.FileStorage):
            has_value = bool(value.filename)
            keep_flag = req_values.get(self.w_fname + '_keepcheck')
            if not has_value and keep_flag == 'yes':
                # no value, but we want to preserve existing one
                return False
            # file field w/ no content
            # TODO: this is not working sometime...
            # return not bool(value.content_length)
            return not has_value
        return super().w_check_empty_value(value, **req_values)


class ImageWidget(models.AbstractModel):
    _name = 'cms.form.widget.image'
    _inherit = 'cms.form.widget.binary.mixin'
    _w_template = 'cms_form.field_widget_image'
