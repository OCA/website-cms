# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import models, tools, fields, api
import os

testing = tools.config.get('test_enable') or os.environ.get('ODOO_TEST_ENABLE')

if testing:
    class SecuredModel(models.Model):
        """A test model that implements `cms.security.mixin`."""

        _name = 'testmodel.secured'
        _description = 'cms_mixin: secured test model'
        _inherit = [
            'website.published.mixin',
            'cms.security.mixin',
        ]
        # generate security automatically
        _auto_security_policy = True

        name = fields.Char()
        image = fields.Binary(attachment=1)

        # TODO: include this fix conditionally in any website model?
        @api.multi
        def unlink(self):
            # drop image attachments before deletion
            # since this commit here
            # https://github.com/odoo/odoo/commit/eb9113c04d66627fbe04b473b9010e5de973c6aa  # noqa
            # prevents a normal portal user to delete the attachment
            # if you are not an employee.
            # Reported issue https://github.com/odoo/odoo/issues/15311
            self.write({'image': False})
            res = super(SecuredModel, self).unlink()
            return res

    class OrderableModel(models.Model):
        """A test model that implements `cms.orderable.mixin`."""

        _name = 'testmodel.orderable'
        _description = 'cms_mixin: orderable test model'
        _inherit = [
            'cms.orderable.mixin',
        ]
        name = fields.Char()

    class CoremetadataModel(models.Model):
        """A test model that implements `cms.coremetadata.mixin`."""

        _name = 'testmodel.coremetadata'
        _description = 'cms_mixin: coremetadata test model'
        _inherit = [
            'website.published.mixin',
            'cms.coremetadata.mixin',
        ]
        name = fields.Char()

    class ContentModel(models.Model):
        """A test model that implements `cms.content.mixin`."""

        _name = 'testmodel.content'
        _description = 'cms_mixin: content test model'
        _inherit = [
            'cms.content.mixin',
        ]
        cms_url_prefix = '/contents/'

    class ParentModel(models.Model):
        """A test model that implements `cms.parent.mixin`."""

        _name = 'testmodel.parent'
        _description = 'cms_mixin: parent test model'
        _inherit = [
            'cms.parent.mixin',
        ]
        name = fields.Char()

        def _open_children_context(self):
            return {'custom_key': 'foo'}
