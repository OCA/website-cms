# -*- coding: utf-8 -*-
# Copyright 2016 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models
from openerp.tools.mimetypes import guess_mimetype

import json
import base64
import werkzeug


def m2o_to_form(form, record, fname, value, **req_values):
    # important: return False if no value
    # otherwise you will compare an empty recordset with an id
    # in a select input in form widget template.
    if isinstance(value, basestring) and value.isdigit():
        # number as string
        return int(value)
    elif isinstance(value, models.BaseModel):
        return value and value.id or None
    return None


def x2many_to_form(form, record, fname, value,
                   display_field='display_name', **req_values):
    value = [{'id': x.id, 'name': x[display_field]} for x in value or []]
    value = json.dumps(value)
    return value


def binary_to_form(form, record, fname, value, **req_values):
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
            mimetype = guess_mimetype(value.decode('base64'))
        _value = {
            'value': value,
            'raw_value': value,
            'mimetype': mimetype,
        }
        if mimetype.startswith('image/'):
            _value['value'] = 'data:{};base64,{}'.format(mimetype, value)
    return _value


def form_to_integer(form, fname, value, **req_values):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def form_to_float(form, fname, value, **req_values):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def form_to_x2many(form, fname, value, **req_values):
    _value = False
    if value:
        ids = [int(rec_id) for rec_id in value.split(',')]
        _value = [(6, False, ids)]
    return _value


def form_to_binary(form, fname, value, **req_values):
    _value = False
    if req_values.get(fname + '_keepcheck') == 'yes':
        # prevent discarding image
        req_values.pop(fname, None)
        req_values.pop(fname + '_keepcheck')
        return None
    if value:
        if hasattr(value, 'read'):
            file_content = value.read()
            _value = base64.encodestring(file_content)
        else:
            _value = value.split(',')[-1]
    return _value


def form_to_date(form, fname, value, **req_values):
    if not value:
        # make sure we do not return empty string which breaks the ORM
        return False
    return value


DEFAULT_LOADERS = {
    'many2one': m2o_to_form,
    'one2many': x2many_to_form,
    'many2many': x2many_to_form,
    'binary': binary_to_form,
    # TODO: use a specific field type for images
    'image': binary_to_form,
}
DEFAULT_EXTRACTORS = {
    'integer': form_to_integer,
    'float': form_to_float,
    'many2one': form_to_integer,
    'one2many': form_to_x2many,
    'many2many': form_to_x2many,
    # TODO: use a specific field type for images
    'image': form_to_binary,
    'binary': form_to_binary,
    'date': form_to_date,
    'datetime': form_to_date,
}
