# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import base64
import werkzeug

from openerp import models
from openerp.tools.mimetypes import guess_mimetype


def ids_from_input(value):
    return [int(rec_id) for rec_id in value.split(',') if rec_id.isdigit()]


def m2o_to_form(form, record, fname, value, **req_values):
    # important: return False if no value
    # otherwise you will compare an empty recordset with an id
    # in a select input in form widget template.
    if isinstance(value, basestring) and value.isdigit():
        # number as string
        return int(value) > 0 and int(value)
    elif isinstance(value, models.BaseModel):
        return value and value.id or None
    return None


def x2many_to_form(form, record, fname, value,
                   display_field='display_name', **req_values):
    if not value:
        return json.dumps([])
    if record and value == record[fname]:
        # value from record
        value = [{'id': x.id, 'name': x[display_field]} for x in value or []]
    elif isinstance(value, basestring) and value == req_values.get(fname):
        # value from request
        # FIXME: the field could come from the form not the model!
        value = form.form_model[fname].browse(
            ids_from_input(value)).read(['name'])
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


def form_to_m2o(form, fname, value, **req_values):
    val = form_to_integer(form, fname, value, **req_values)
    # we don't want m2o value do be < 1
    return val > 0 and val or None


def form_to_float(form, fname, value, **req_values):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def form_to_x2many(form, fname, value, **req_values):
    _value = False
    if form._form_extract_value_mode == 'write':
        if value:
            _value = [(6, False, ids_from_input(value))]
        else:
            # wipe them
            _value = [(5, )]
    else:
        _value = value and ids_from_input(value) or []
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


TRUE_VALUES = ('on', 'yes', 'ok', 'true', True, 1, '1', )


def form_to_bool(form, fname, value, **req_values):
    return value in TRUE_VALUES


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
    'many2one': form_to_m2o,
    'one2many': form_to_x2many,
    'many2many': form_to_x2many,
    # TODO: use a specific field type for images
    'image': form_to_binary,
    'binary': form_to_binary,
    'date': form_to_date,
    'datetime': form_to_date,
    'boolean': form_to_bool,
}


def data_merge(a, b):
    """Merges b into a and return merged result

    NOTE: tuples and arbitrary objects are not handled
    as it is totally ambiguous what should happen.

    Thanks to http://stackoverflow.com/a/15836901/647924
    """
    key = None
    # ## debug output
    # sys.stderr.write("DEBUG: %s to %s\n" %(b,a))
    try:
        if a is None or isinstance(a, (str, unicode, int, long, float)):
            # border case for first run or if a is a primitive
            a = b
        elif isinstance(a, list):
            # lists can be only appended
            if isinstance(b, list):
                # merge lists
                a.extend(b)
            else:
                # append to list
                a.append(b)
        elif isinstance(a, dict):
            # dicts must be merged
            if isinstance(b, dict):
                for key in b:
                    if key in a:
                        a[key] = data_merge(a[key], b[key])
                    else:
                        a[key] = b[key]
            else:
                raise Exception(
                    'Cannot merge non-dict "%s" into dict "%s"' % (b, a))
        else:
            raise Exception('NOT IMPLEMENTED "%s" into "%s"' % (b, a))
    except TypeError, e:
        raise Exception(
            'TypeError "%s" in key "%s" '
            'when merging "%s" into "%s"' % (e, key, b, a))
    return a
