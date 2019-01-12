# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import werkzeug
import base64

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
        if value:
            if isinstance(value, werkzeug.datastructures.FileStorage):
                # value from request, we cannot set a value for input field
                value = ''
                mimetype = ''
            else:
                value = str(value, 'utf-8')
                mimetype = guess_mimetype(base64.b64decode(value))
            _value = {
                'value': value,
                'raw_value': value,
                'mimetype': mimetype,
            }
            if mimetype.startswith('image/'):
                _value['value'] = 'data:{};base64,{}'.format(mimetype, value)
        return _value

    def w_extract(self, **req_values):
        value = super().w_extract(**req_values)
        return self.form_to_binary(value, **req_values)

    def form_to_binary(self, value, **req_values):
        _value = False
        if req_values.get(self.w_fname + '_keepcheck') == 'yes':
            # prevent discarding image
            req_values.pop(self.w_fname, None)
            req_values.pop(self.w_fname + '_keepcheck')
            return None
        if value:
            if hasattr(value, 'read'):
                file_content = value.read()
                _value = base64.encodestring(file_content)
            else:
                _value = value.split(',')[-1]
        return _value


class ImageWidget(models.AbstractModel):
    _name = 'cms.form.widget.image'
    _inherit = 'cms.form.widget.binary.mixin'
    _w_template = 'cms_form.field_widget_image'
