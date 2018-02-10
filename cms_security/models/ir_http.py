# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import models
from odoo.addons.website.models import ir_http
from .security import CMSSecurityMixin
from werkzeug.exceptions import NotFound


class SecureModelConverter(ir_http.ModelConverter):
    """A new model converter w/ security check.

    The base model converter is responsible of converting a slug
    to a real browse object. It works fine except that
    it raises permissions errors only when you access instance fields
    in the template.

    We want to intercept this on demand and apply security check,
    so that whichever model exposes `cms.security.mixin`
    capabilities and uses this route converter,
    will be protected based on mixin behaviors.

    You can use it as usual like this:

        @http.route(['/foo/<model("my.model"):main_object>'])
    """

    def to_python(self, value):
        """Get python record and check it.

        If no permission here, just raise a NotFound!
        """
        record = super().to_python(value)
        if isinstance(record, CMSSecurityMixin) \
                and not record.check_permission(mode='read'):
            raise NotFound()
        return record


class IRHTTP(models.AbstractModel):
    """Override to add our model converter.

    The new model converter make sure to apply security checks.

    See `website.models.ir_http` for default implementation.
    """

    _inherit = 'ir.http'

    @classmethod
    def _get_converters(cls):
        conv = super()._get_converters()
        conv.update({
            'model': SecureModelConverter
        })
        return conv
