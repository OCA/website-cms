# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models

from ... import utils


class IntegerWidget(models.AbstractModel):
    _name = 'cms.form.widget.integer'
    _inherit = 'cms.form.widget.char'

    def w_extract(self, **req_values):
        value = super().w_extract(**req_values)
        return utils.safe_to_integer(value)


class FloatWidget(models.AbstractModel):
    _name = 'cms.form.widget.float'
    _inherit = 'cms.form.widget.char'

    def w_extract(self, **req_values):
        value = super().w_extract(**req_values)
        return utils.safe_to_float(value)
