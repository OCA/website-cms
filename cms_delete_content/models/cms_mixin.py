# Copyright 2017-2018 Camptocamp - Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import _, models


class CMSInfoMixin(models.AbstractModel):
    _inherit = "cms.info.mixin"

    def msg_content_delete_confirm(self):
        self.ensure_one()
        return _("Are you sure you want to delete this item?")

    def msg_content_deleted(self):
        self.ensure_one()
        return _("%s deleted.") % self._description
