# Copyright 2023 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import json

from odoo.addons.base_sparse_field.models.fields import Serialized as BaseSerialized


class Serialized(BaseSerialized):
    """Better implementation of Serialized field.

    1. load proper default (core always load {})
    2. do not fail if value is already a py obj
    TODO: propose to odoo core
    """

    def convert_to_record(self, value, record):
        default = (
            self.default(self.model_name) if callable(self.default) else self.default
        )
        # Important: if you want to set an empty value and bypass the default
        # you must use a string (eg: "[]" or "{}")
        value = value if value is not None else default
        if isinstance(value, str):
            return json.loads(value)
        return value
