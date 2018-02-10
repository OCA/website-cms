# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import models, fields, api, SUPERUSER_ID, tools
from odoo.http import request
from .. import utils

import os
import logging
logger = logging.getLogger(__name__)


TEST_ENABLED = tools.config.get('test_enable') or os.getenv('ODOO_TEST_ENABLE')


class CMSSecurityMixin(models.AbstractModel):
    """Provide basic logic for protecting website items.

    TODO: explain in detail what we do.
    """

    _name = "cms.security.mixin"
    _description = "A mixin for protecting website content"
    # internal flag to enable/disable auto creation of ACL + security rules
    _cms_auto_security_policy = False

    read_group_ids = fields.Many2many(
        string='View Groups',
        comodel_name='res.groups',
        help=("Allow `view` access to this item to specific groups. "
              u"No group means anybody with proper rights can see it.")
    )
    write_group_ids = fields.Many2many(
        string='Write Groups',
        comodel_name='res.groups',
        help=("Allow `write` access to this item to specific groups. "
              u"No group means anybody with proper rights can edit it.")
    )

    def _auto_rule_name_prefix(self):
        """Return name prefix for automatic rules."""
        return 'cms_security_{}'.format(self._name.replace('.', '_'))

    def _auto_get_model_id(self):
        """Return ID for current model for automatic rules."""
        self.env.cr.execute(
            "SELECT id FROM ir_model WHERE model = %s", (self._name, ))
        res = self.env.cr.fetchone()
        return res[0] if res else None

    def _auto_access_values(self, env, model_id):
        """Return automatic ACL rules values."""
        prefix = self._auto_rule_name_prefix()
        return utils.build_ACL_values(env, prefix, model_id)

    def _auto_create_access(self, model_id):
        """Create automatic ACL."""
        env = self.env
        for values in self._auto_access_values(env, model_id):
            xmlid = values.pop('_xmlid')
            if not env.ref(xmlid, raise_if_not_found=0):
                record = env['ir.model.access'].create(values)
                utils.add_xmlid(env, record, xmlid)
                logger.info('Created default ACL for %s: %s',
                            self._name, values['name'])

    def _auto_rule_values(self, env, model_id):
        """Return automatic record rules values."""
        prefix = self._auto_rule_name_prefix()
        return utils.build_rule_values(env, prefix, model_id)

    def _auto_create_rule(self, model_id):
        """Create automatic record rules."""
        env = self.env
        for values in self._auto_rule_values(env, model_id):
            xmlid = values.pop('_xmlid')
            if not env.ref(xmlid, raise_if_not_found=0):
                record = env['ir.rule'].create(values)
                utils.add_xmlid(env, record, xmlid)
                logger.info('Created default record rule for %s: %s',
                            self._name, values['name'])

    @api.model
    def _setup_complete(self):     # pylint: disable=R8110
        """Override to handle automatic security."""
        super()._setup_complete()
        # TODO: this code runs 2 times on every reboot.
        # `must_create_table` is True on 1st run (!!!)
        # It means that if you delete an ACL or RR is going to be re-created.
        # Any good way to make security setup only once?
        # TODO 2: shall we delete all security records on unistall?
        must_create_table = not tools.table_exists(self._cr, self._table)
        if must_create_table and self._cms_auto_security_policy and self._auto:
            model_id = self._auto_get_model_id()
            if not model_id:
                # TODO: double check this w/ some model-setup guru.
                # `_reflect` creates the `ir.model` record
                # that we need to create ACL and RR.
                # Here we call it only for tests
                # because it seems that `ir.model` record
                # is not create for our fake models.
                if TEST_ENABLED:
                    self._reflect()
                    model_id = self._auto_get_model_id()
            if model_id:
                # at 1st init the model is not there yet
                self._auto_create_access(model_id)
                self._auto_create_rule(model_id)

    @api.model
    def check_permission(self, mode='read', raise_exception=False):
        """Check permission on given object on both ACL and rules.

        :param `obj`: the item to check.
            If not `obj` is passed `self` will be used.
        :param `mode`: the permission mode to check.

        Mainly used for the route converter.
        """
        obj = self
        if request.session.uid:
            obj = obj.with_env(self.env(user=request.session.uid))
        else:
            obj = obj.with_env(request.env)
        if obj.env.user.id == SUPERUSER_ID:
            return True
        try:
            obj.check_access_rights(mode)
            obj.check_access_rule(mode)
            can = True
        except Exception:
            if raise_exception:
                raise
            can = False
        return can

    @api.multi
    def unlink(self):
        """Drop binary attachments before deletion.

        Since this commit here

        https://github.com/odoo/odoo/commit/eb9113c04d66627fbe04b473b9010e5de973c6aa  # noqa

        prevents a normal portal user to delete attachments
        if you are not an employee.

        Reported issue https://github.com/odoo/odoo/issues/15311
        In v11 this is still not working properly :(

        We can assume that if you are deleting a record
        you have the rights to write on it.
        So, here we retrieve all binary fields w/ attachments
        and wipe them before deleting the main record (tests included).
        """
        attachment_fields_to_wipe = {}
        for fname, finfo in self.fields_get().items():
            if finfo['type'] == 'binary' and finfo['attachment']:
                attachment_fields_to_wipe[fname] = False
        self.write(attachment_fields_to_wipe)
        return super().unlink()
