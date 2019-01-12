# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class HiddenWidget(models.AbstractModel):
    _name = 'cms.form.widget.hidden'
    _inherit = 'cms.form.widget.mixin'
    _w_template = 'cms_form.field_widget_hidden'

    @property
    def w_html_fname(self):
        """Field name for final HTML markup."""
        # TODO: use this for all fields and get rid of custom w_extract
        # where possible
        marshaller = ''
        if self.w_field['type'] in ('many2one', 'integer'):
            marshaller = ':int'
        elif self.w_field['type'] in ('float', ):
            marshaller = ':float'
        elif self.w_field['type'] == 'selection' and self.w_field['selection']:
            first_value = self.w_field['selection'][0][0]
            # fields.Selection does the same check to determine PG col type
            if isinstance(first_value, int):
                marshaller = ':int'
            elif isinstance(first_value, float):
                marshaller = ':float'
        return self.w_fname + marshaller
