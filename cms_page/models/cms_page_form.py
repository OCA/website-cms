# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import models


class CMSPageForm(models.AbstractModel):

    _name = 'cms.form.cms.page'
    _inherit = 'cms.form'
    _form_model = 'cms.page'
    _form_model_fields = (
        'name',
        'description',
        'type_id',
        'view_id',
    )
    _form_fields_order = (
        'name',
        'description',
        'type_id',
        'view_id',
    )


class CMSPageSearchForm(models.AbstractModel):

    _name = 'cms.form.search.cms.page'
    _inherit = 'cms.form.search'
    _form_model = 'cms.page'
    _form_model_fields = (
        'name',
    )
