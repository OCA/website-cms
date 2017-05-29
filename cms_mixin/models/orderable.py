# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from openerp import models, fields, api


class CMSOrderableMixin(models.AbstractModel):
    """Orderable mixin to allow sorting of objects.

    Add a sequence field that you can use for sorting items
    in tree views. Add the field to a view like this:

        <field name="sequence" widget="handle" />

    Default sequence is calculated as last one + 1.
    """

    _name = "cms.orderable.mixin"
    _description = "A mixin for providing sorting features"
    _order = 'sequence desc, id'

    sequence = fields.Integer(
        'Sequence',
        required=True,
        default=lambda self: self._default_sequence()
    )

    @api.model
    def _default_sequence(self):
        last = self.search([], limit=1, order='sequence desc')
        if not last:
            return 0
        return last.sequence + 1
