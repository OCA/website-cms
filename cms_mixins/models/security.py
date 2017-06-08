# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from openerp import models, fields, api, SUPERUSER_ID
from openerp.http import request
from openerp.addons.website.models import ir_http

from werkzeug.exceptions import NotFound

import logging
logger = logging.getLogger('[CMSSecurityMixin]')


def add_xmlid(env, record, xmlid, noupdate=False):
    """ Add a XMLID on an existing record """
    if '.' in xmlid:
        module, name = xmlid.split('.')
    else:
        module = ''
        name = xmlid
    return env['ir.model.data'].create({
        'name': name,
        'module': module,
        'model': record._name,
        'res_id': record.id,
        'noupdate': noupdate,
    })


class CMSSecurityMixin(models.AbstractModel):
    """Provide basic logic for protecting website items."""

    _name = "cms.security.mixin"
    _description = "A mixin for protecting website content"
    # internal flag to enable/disable auto creation of security rules
    _auto_security_policy = False

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
        return 'cms_security_auto_{}'.format(self._name.replace('.', '_'))

    def _auto_get_model_id(self, cr):
        """Return ID for current model for automatic rules."""
        cr.execute("select id from ir_model where model = %s", (self._name, ))
        res = cr.fetchone()
        return res[0] if res else None

    def _auto_access_values(self, model_id, env):
        """Return automatic ACL rules values."""
        prefix = self._auto_rule_name_prefix()
        values = [
            {
                # allow all to manage content
                # we limit this in record rule
                '_xmlid': '__auto__.' + prefix + '_all',
                'name': prefix + ' all',
                'model_id': model_id,
                'perm_read': 1,
                'perm_create': 1,
                'perm_write': 1,
                'perm_unlink': 1,
                'active': True,
            },
        ]
        return values

    def _auto_create_access(self, cr, model_id):
        """Create automatic ACL."""
        env = api.Environment(cr, SUPERUSER_ID, {})
        for values in self._auto_access_values(model_id, env):
            xmlid = values.pop('_xmlid')
            if not env.ref(xmlid, raise_if_not_found=0):
                record = env['ir.model.access'].create(values)
                add_xmlid(env, record, xmlid)
                logger.info('Created default ACL for %s: %s',
                            self._name, values['name'])

    def _auto_rule_values(self, model_id, env):
        """Return automatic record rules values."""
        prefix = self._auto_rule_name_prefix()
        descr1 = 'published and owner can view'
        descr2 = 'only owner can write'
        descr3 = 'allowed groups can view (read_group_ids)'
        descr4 = 'allowed groups can write (write_group_ids)'
        # TODO: move this stuff to xml templates
        values = [
            {
                '_xmlid': '__auto__.{}_{}'.format(
                    prefix, descr1.replace(' ', '_')),
                'name': '{} {}'.format(prefix, descr1),
                'domain_force': """
                    ['|',
                     ('website_published', '=', True),
                     '&', ('create_uid','=',user.id),
                          ('website_published', '=', False)
                    ]
                """,
                'active': True,
                'perm_read': True,
                'perm_write': False,
                'perm_create': False,
                'perm_unlink': False,
                'model_id': model_id,
                'groups': [
                    (4, env.ref('base.group_portal').id),
                    (4, env.ref('base.group_public').id),
                ],
            },
            {
                '_xmlid': '__auto__.{}_{}'.format(
                    prefix, descr2.replace(' ', '_')),
                'name': '{} {}'.format(prefix, descr2),
                'domain_force': """
                    [('create_uid','=',user.id)]
                """,
                'active': True,
                'perm_write': True,
                'perm_read': False,
                'perm_create': False,
                'perm_unlink': True,
                'model_id': model_id,
                'groups': [
                    (4, env.ref('base.group_portal').id),
                    (4, env.ref('base.group_public').id),
                ],
            },
            {
                '_xmlid': '__auto__.{}_{}'.format(
                    prefix, descr3.replace(' ', '_')),
                'name': '{} {}'.format(prefix, descr3),
                'domain_force': """
                    [('read_group_ids', '!=', False),
                     ('read_group_ids', 'in', user.groups_id.ids),]
                """,
                'active': True,
                'perm_write': False,
                'perm_read': True,
                'perm_create': False,
                'perm_unlink': False,
                'model_id': model_id,
                'groups': [
                    (4, env.ref('base.group_portal').id),
                    (4, env.ref('base.group_public').id),
                ],
            },
            {
                '_xmlid': '__auto__.{}_{}'.format(
                    prefix, descr4.replace(' ', '_')),
                'name': '{} {}'.format(prefix, descr4),
                'domain_force': """
                    [('write_group_ids', '!=', False),
                     ('write_group_ids', 'in', user.groups_id.ids),]
                """,
                'active': True,
                'perm_write': True,
                'perm_read': False,
                'perm_create': False,
                'perm_unlink': False,
                'model_id': model_id,
                'groups': [
                    (4, env.ref('base.group_portal').id),
                    (4, env.ref('base.group_public').id),
                ],
            },
        ]
        return values

    def _auto_create_rule(self, cr, model_id):
        """Create automatic record rules."""
        env = api.Environment(cr, SUPERUSER_ID, {})
        for values in self._auto_rule_values(model_id, env):
            xmlid = values.pop('_xmlid')
            if not env.ref(xmlid, raise_if_not_found=0):
                record = env['ir.rule'].create(values)
                add_xmlid(env, record, xmlid)
                logger.info('Created default record rule for %s: %s',
                            self._name, values['name'])

    def _setup_complete(self, cr, uid):     # pylint: disable=R8110
        """Override to handle automatic security."""
        if self._auto_security_policy and self._auto:
            model_id = self._auto_get_model_id(cr)
            if model_id:
                # at 1st init the model is not there yet
                self._auto_create_access(cr, model_id)
                self._auto_create_rule(cr, model_id)
        return super(CMSSecurityMixin, self)._setup_complete(cr, uid)

    @api.model
    def check_permission(self, mode='view', raise_exception=False):
        """Check permission on given object on both ACL and rules.

        @param `obj`: the item to check.
        If not `obj` is passed `self` will be used.

        @param `mode`: the permission mode to check.
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
        record = super(SecureModelConverter, self).to_python(value)
        if isinstance(record, CMSSecurityMixin) \
                and not record.check_permission(mode='view'):
            raise NotFound()
        return record


class IRHTTP(models.AbstractModel):
    """Override to add our model converter.

    The new model converter make sure to apply security checks.

    See `website.models.ir_http` for default implementation.
    """

    _inherit = 'ir.http'

    def _get_converters(self):
        return dict(
            super(IRHTTP, self)._get_converters(),
            model=SecureModelConverter,
        )
