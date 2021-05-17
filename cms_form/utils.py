# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


def safe_to_integer(value, **kw):
    """Convert to integer safely."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def safe_to_float(value, **kw):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def safe_to_date(value, **kw):
    if not value:
        # 1. make sure we do not return empty string which breaks the ORM
        # 2. return `None` so that request extractor ignores the field
        # if it's not required
        return None
    return value


TRUE_VALUES = ('on', 'yes', 'ok', 'true', True, 1, '1', )


def string_to_bool(value, true_values=TRUE_VALUES):
    return value in true_values


def data_merge(a, b):
    """Merges `b` into `a` and return merged result

    NOTE: tuples and arbitrary objects are not handled
    as it is totally ambiguous what should happen.

    Thanks to http://stackoverflow.com/a/15836901/647924
    """
    key = None
    try:
        if a is None or isinstance(a, (str, int, float)):
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
                raise ValueError(
                    'Cannot merge non-dict "%s" into dict "%s"' % (b, a)
                )
        else:
            raise NotImplementedError(
                'NOT IMPLEMENTED "%s" into "%s"' % (b, a)
            )
    except TypeError as e:  # pragma: no cover
        raise TypeError(
            '"%s" in key "%s" when merging "%s" into "%s"' % (e, key, b, a)
        )
    return a
