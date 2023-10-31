# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import base64
import html
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import werkzeug

from odoo.tools import pycompat
from odoo.tools.mimetypes import guess_mimetype

from . import utils


def marshal_request_values(values):
    """Transform given request values using marshallers.

    Available marshallers: see Marshaller class.
    """
    return Marshaller(values).marshall()


@dataclass
class Todo:
    okey: str
    oval: Any
    handlers: list[Callable]


class Marshaller:
    def __init__(self, req_values):
        self.req_values = req_values
        self.todos = []
        self.skip_keys = {"csrf_token"}
        self._collect_todo()

    def _add_todo(self, orig_key, orig_value, *handlers):
        self.todos.append(Todo(okey=orig_key, oval=orig_value, handlers=handlers))

    def _collect_todo(self):
        done = set()
        for k, v in self.req_values.items():
            if k in self.skip_keys:
                continue
            for operator, handler in self._marshallers():
                if k.endswith(operator):
                    self._add_todo(k, v, handler)
                    done.add(k)
                    continue
            # plain
            if k not in done:
                self._add_todo(k, v, self.marshal_plain)
                done.add(k)

    def _marshallers(self):
        # TODO: add docs
        # TODO: support combinations like `:list:int` or `:dict:int`
        return (
            (":esc", self.marshal_esc),
            (":dict:list", self.marshal_dict_list),
            (":list", self.marshal_list),
            (":dict", self.marshal_dict),
            (":int", self.marshal_int),
            (":float", self.marshal_float),
            (":file", self.marshal_file),
        )

    def marshall(self):
        res = {}
        for todo in self.todos:
            k, v = todo.okey, todo.oval
            for handler in todo.handlers:
                k, v = handler(k, v)
            res[k] = v
        return res

    def marshal_plain(self, orig_key, orig_value):
        """No transform."""
        return orig_key, orig_value

    def marshal_esc(self, orig_key, orig_value):
        """Transform `foo:esc` inputs to escaped value."""
        k = orig_key[: -len(":esc")]
        v = html.escape(orig_value)
        return k, v

    def marshal_list(self, orig_key, orig_value):
        """Transform `foo:list` inputs to list of values."""
        k = orig_key[: -len(":list")]
        v = self.req_values.getlist(orig_key)
        return k, v

    def marshal_int(self, orig_key, orig_value):
        """Transform `foo:int` inputs to integer values."""
        k = orig_key[: -len(":int")]
        return k, utils.safe_to_integer(orig_value)

    def marshal_float(self, orig_key, orig_value):
        """Transform `foo:float` inputs to float values."""
        k = orig_key[: -len(":float")]
        return k, utils.safe_to_float(orig_value)

    def marshal_dict(self, orig_key, orig_value):
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
        key = orig_key.split(".")[0]
        for _k, _v in self.req_values.items():
            # get all the keys matching fname
            if not _k.startswith(key):
                continue
            # TODO: `__` will be to support extra marshallers, like:
            # foo.1:dict:int -> get a dictionary w/ integer values
            full_key, _, __ = _k.partition(":dict")
            res[full_key.split(".")[-1]] = _v
        return key, res

    def marshal_dict_list(self, orig_key, orig_value):
        """Transform `foo:dict:list` inputs to list of dict values.

        `orig_key` must be formatted like:

            `$fname.$index.$dict_key:dict:list`

        Every request key matching `$fname` prefix
        will be merged into a list of dicts whereas keys will match all `$dict_key`
        and the position in the list will match $index.

        Example:

            values = [
                ("b.1.x:dict:list", "b1x"),
                ("b.1.y:dict:list", "b1y"),
                ("b.2.x:dict:list", "b2x"),
                ("b.2.y:dict:list", "b2y"),
            ]

            will be translated to:

            values['b'] = [
                {
                    'x': 'b1x',
                    'y': 'b1y',
                },
                {
                    'x': 'b2x',
                    'y': 'b2y',
                },
            }

        """
        res = []

        def parse_key(key):
            main_key, index, inner_key = key[: -len(":dict:list")].split(".")
            if not index.isdigit():
                raise ValueError(":dict:list requires an integer index")
            return main_key, int(index), inner_key

        main_key, index, inner_key = parse_key(orig_key)
        by_index = {}
        for _k, _v in self.req_values.items():
            # get all the keys matching fname
            if not _k.startswith(f"{main_key}."):
                continue
            self.skip_keys.add(_k)
            __, index, inner_key = parse_key(_k)
            by_index.setdefault(index, []).append((inner_key, _v))
        #  by_index = {0: [(x, xv), (y, yv)]}
        for __, values in sorted(by_index.items()):
            item = {}
            for inner_key, value in values:
                item[inner_key] = value
            res.append(item)
        return main_key, res

    def marshal_file(self, orig_key, orig_value):
        k = orig_key[: -len(":file")]
        value = orig_value
        if isinstance(value, werkzeug.datastructures.FileStorage):
            _value = self._filedata_from_filestorage(value)
        else:
            mimetype = guess_mimetype(value)
            _value = {
                "value": value,
                "raw_value": value,
                "mimetype": mimetype,
                "content_type": mimetype,
            }
        _value["_from_request"] = True
        return k, _value

    @staticmethod
    def _filedata_from_filestorage(fs):
        raw_value = fs.read()
        value = base64.b64encode(raw_value)
        value = pycompat.to_text(value)
        data = dict(raw_value=value, value=value)
        for attr in (
            "content_length",
            "content_type",
            "filename",
            "headers",
            "mimetype",
            "mimetype_params",
        ):
            data[attr] = getattr(fs, attr)
        return data
