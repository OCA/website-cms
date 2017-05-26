# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


def safe_to_integer(value, **kw):
    """Convert to integer safely."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def safe_to_float(value, **kw):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def safe_to_date(value, **kw):
    if not value:
        # make sure we do not return empty string which breaks the ORM
        return False
    return value


TRUE_VALUES = ('on', 'yes', 'ok', 'true', True, 1, '1', )


def string_to_bool(value, true_values=TRUE_VALUES):
    return value in true_values


# DEFAULT_LOADERS = {
#     'many2one': m2o_to_form,
#     'one2many': x2many_to_form,
#     'many2many': x2many_to_form,
#     'binary': binary_to_form,
#     # TODO: use a specific field type for images
#     'image': binary_to_form,
# }
# DEFAULT_EXTRACTORS = {
#     'integer': form_to_integer,
#     'float': form_to_float,
#     'many2one': form_to_m2o,
#     'one2many': form_to_x2many,
#     'many2many': form_to_x2many,
#     # TODO: use a specific field type for images
#     'image': form_to_binary,
#     'binary': form_to_binary,
#     'date': form_to_date,
#     'datetime': form_to_date,
#     'boolean': form_to_bool,
# }
#

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
