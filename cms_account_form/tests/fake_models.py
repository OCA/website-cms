# Copyright 2018 Simone Orsi - Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import exceptions, models


class FakePartnerOverride(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    # we are extending a real model: do not delete it
    _teardown_no_delete = True

    def check_vat(self):
        """Simulate `base_vat.check_vat`.

        `base_vat` is not installed by default and
        VAT validation checks if this method is present.
        Here we simulate it and we let it fail on demand.
        """
        if self.env.context.get('test_do_fail'):
            raise exceptions.ValidationError('VAT check failed')  # noqa MQT
