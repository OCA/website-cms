# Copyright 2023 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import json
import logging

from odoo.addons.base_sparse_field.models.fields import Serialized as BaseSerialized

_logger = logging.getLogger(__name__)


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
            try:
                return json.loads(value)
            except ValueError:
                _logger.error("%s got bad json string: %s", self.name, value)
                # Likely a string that is not convert-able.
                # Consider using a special encoder/decoder.
                return value

        return value
