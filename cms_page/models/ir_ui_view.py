# -*- coding: utf-8 -*-

from openerp import models
from openerp import fields
from openerp import api
from openerp.addons.web.http import request
from openerp.addons.website.models.website import url_for as url_for_orig


def url_for(path_or_uri, lang=None, main_object=None):
    """Override to avoid building links for not translated contents."""
    if main_object and main_object._name == 'cms.page':
        if lang and not lang == request.website.default_lang_code \
                and not request.params.get('edit_translations') \
                and not request.website.is_publisher():
            # avoid building URLs for not translated contents
            # unless we are translating it
            avail_transl = main_object.get_translations()
            if lang not in avail_transl:
                return '/' + lang

    return url_for_orig(path_or_uri, lang=lang)


class IRUIView(models.Model):
    _inherit = "ir.ui.view"

    cms_view = fields.Boolean(
        'CMS view?',
        help="This view will be available as a CMS view."
    )
    # TODO: configure default view per type
    # cms_default_type_ids = fields.Many2many()
    # cms_sidebar = fields.Boolean(
    #     'CMS sidebar?',
    #     help="This view will be available as a CMS sidebar view."
    # )

    @api.model
    def _prepare_qcontext(self):
        """Override to inject our custom rendering variables."""
        qcontext = super(IRUIView, self)._prepare_qcontext()
        qcontext['url_for'] = url_for
        # qcontext['is_cms_manager'] = \
        #     self.env.user.has_group('cms_page.cms_manager')
        return qcontext
