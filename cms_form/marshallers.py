# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import werkzeug.utils


def marshal_request_values(values):
    """Transform given request values using marshallers.

    Available marshallers:

    * `:int` transform to integer
    * `:float` transform to float
    * `:list` transform to list of values
    * `:dict` transform to dictionary of values
    """
    # TODO: add docs
    # TODO: support combinations like `:list:int` or `:dict:int`
    res = {}
    for k, v in values.items():
        v = werkzeug.utils.escape(v)
        if k in ('csrf_token', ):
            continue
        # fields w/ multiple values
        if k.endswith(':list'):
            k, v = marshal_list(values, k, v)
            res[k] = v
            continue
        if k.endswith(':dict'):
            k, v = marshal_dict(values, k, v)
            res[k] = v
            continue
        if k.endswith(':int'):
            k, v = marshal_int(values, k, v)
            res[k] = v
            continue
        if k.endswith(':float'):
            k, v = marshal_float(values, k, v)
            res[k] = v
            continue
        res[k] = v
    return res


def marshal_list(values, orig_key, orig_value):
    """Transform `foo:list` inputs to list of values."""
    k = orig_key[:-len(':list')]
    v = values.getlist(orig_key)
    return k, v


def marshal_int(values, orig_key, orig_value):
    """Transform `foo:int` inputs to integer values."""
    k = orig_key[:-len(':int')]
    v = int(orig_value) if orig_value and orig_value.isdigit() else orig_value
    return k, v


def marshal_float(values, orig_key, orig_value):
    """Transform `foo:float` inputs to float values."""
    k = orig_key[:-len(':float')]
    try:
        v = float(orig_value.replace(',', '.'))
    except (ValueError, TypeError):
        v = orig_value
    return k, v


def marshal_dict(values, orig_key, orig_value):
    """Transform `foo:dict` inputs to dictionary values.

    `orig_key` must be formatted like:

        `$fname.$dict_key:dict`

    Every request key matching `$fname` prefix
    will be merged into a dict whereas keys will match all `$dict_key`.

    Example:

        values = [
            ('foo.a:dict', '1'),
            ('foo.b:dict', '2'),
            ('foo.c:dict', '3'),
        ]

        will be translated to:

        values['foo'] = {
            'a': '1',
            'b': '2',
            'c': '3',
        }

    """
    res = {}
    key = orig_key.split('.')[0]
    for _k, _v in values.items():
        # get all the keys matching fname
        if not _k.startswith(key):
            continue
        # TODO: `__` will be to support extra marshallers, like:
        # foo.1:dict:int -> get a dictionary w/ integer values
        full_key, _, __ = _k.partition(':dict')
        res[full_key.split('.')[-1]] = _v
    return key, res
