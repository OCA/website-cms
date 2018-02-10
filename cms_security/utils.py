# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo.addons.http_routing.models.ir_http import slugify


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


def make_xmlid(prefix, name):
    return '__auto__.{}_{}'.format(
        prefix, slugify(name).replace('-', '_'))


def build_ACL_values(env, prefix, model_id):
    values = [{
        # allow all portal users to manage content
        # we limit this in record rule
        '_xmlid': '__auto__.' + prefix + '_all',
        'name': prefix + ' all',
        'model_id': model_id,
        'perm_read': 1,
        'perm_create': 0,
        'perm_write': 0,
        'perm_unlink': 0,
        'active': True,
    }, {
        # allow all portal users to manage content
        # we limit this in record rule
        '_xmlid': '__auto__.' + prefix + '_portal',
        'name': prefix + ' portal',
        'model_id': model_id,
        'perm_read': 1,
        'perm_create': 1,
        'perm_write': 1,
        'perm_unlink': 1,
        'group_id': env.ref('base.group_portal').id,
        'active': True,
    }, ]
    return values


def build_rule_values(env, prefix, model_id):
    """Build 4 RR values."""

    rr1 = 'can view only if published or owner'
    rr2 = 'only owner can write'
    rr3 = 'allowed groups can view (read_group_ids)'
    rr4 = 'allowed groups can write (write_group_ids)'
    values = [{
        '_xmlid': make_xmlid(prefix, rr1),
        'name': '{} {}'.format(prefix, rr1),
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
    }, {
        '_xmlid': make_xmlid(prefix, rr2),
        'name': '{} {}'.format(prefix, rr2),
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
        ],
    }, {
        '_xmlid': make_xmlid(prefix, rr3),
        'name': '{} {}'.format(prefix, rr3),
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
        ],
    }, {
        '_xmlid': make_xmlid(prefix, rr4),
        'name': '{} {}'.format(prefix, rr4),
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
        ],
    }, ]
    return values
