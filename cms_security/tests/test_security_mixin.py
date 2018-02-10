# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)


import odoo.tests.common as test_common


class TestSecurityMixin(test_common.SavepointCase):

    at_install = False
    post_install = True

    @property
    def sec_mixin(self):
        return self.env['cms.security.mixin']

    def _get_model_id(self):
        # just a fake a ID
        return 999

    def test_new_fields(self):
        self.assertIn('read_group_ids', self.sec_mixin)
        self.assertIn('write_group_ids', self.sec_mixin)

    def test_auto_rule_name_prefix(self):
        self.assertEqual(
            self.sec_mixin._auto_rule_name_prefix(),
            'cms_security_cms_security_mixin'
        )

    def test_auto_access_values(self):
        model_id = self._get_model_id()
        values = self.sec_mixin._auto_access_values(self.env, model_id)
        self.assertEqual(len(values), 2)
        self.assertDictEqual(values[0], {
            '_xmlid': '__auto__.cms_security_cms_security_mixin_all',
            'name': 'cms_security_cms_security_mixin all',
            'model_id': self._get_model_id(),
            'perm_read': 1,
            'perm_create': 0,
            'perm_write': 0,
            'perm_unlink': 0,
            'active': True,
        })
        self.assertDictEqual(values[1], {
            '_xmlid': '__auto__.cms_security_cms_security_mixin_portal',
            'name': 'cms_security_cms_security_mixin portal',
            'model_id': self._get_model_id(),
            'perm_read': 1,
            'perm_create': 1,
            'perm_write': 1,
            'perm_unlink': 1,
            'active': True,
            'group_id': self.env.ref('base.group_portal').id,
        })

    def _assert_values_equal(self, values, expected):

        def flatten_domain(v):
            v = ','.join([x.strip() for x in v.split(',')])
            v = ''.join([x.strip() for x in v.splitlines()])
            return v

        for k, v in values.items():
            exp_v = expected[k]
            if k == 'domain_force':
                v = flatten_domain(v)
                exp_v = flatten_domain(exp_v)
            self.assertEqual(
                v, exp_v, '`{}`:\n`{}`\n!=\n`{}`'.format(k, v, exp_v))

    def test_record_rule_value1(self):
        model_id = self._get_model_id()
        values = self.sec_mixin._auto_rule_values(self.env, model_id)[0]
        expected = {
            '_xmlid':
                '__auto__.cms_security_cms_security_mixin_'
                'can_view_only_if_published_or_owner',
            'name':
                'cms_security_cms_security_mixin '
                'can view only if published or owner',
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
                (4, self.env.ref('base.group_portal').id),
                (4, self.env.ref('base.group_public').id),
            ],
        }
        self._assert_values_equal(values, expected)

    def test_record_rule_value2(self):
        model_id = self._get_model_id()
        values = self.sec_mixin._auto_rule_values(self.env, model_id)[1]
        expected = {
            '_xmlid':
                '__auto__.cms_security_cms_security_mixin_'
                'only_owner_can_write',
            'name':
                'cms_security_cms_security_mixin '
                'only owner can write',
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
                (4, self.env.ref('base.group_portal').id),
            ],
        }
        self._assert_values_equal(values, expected)

    def test_record_rule_value3(self):
        model_id = self._get_model_id()
        values = self.sec_mixin._auto_rule_values(self.env, model_id)[2]
        expected = {
            '_xmlid':
                '__auto__.cms_security_cms_security_mixin_'
                'allowed_groups_can_view_read_group_ids',
            'name':
                'cms_security_cms_security_mixin '
                'allowed groups can view (read_group_ids)',
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
                (4, self.env.ref('base.group_portal').id),
            ],
        }
        self._assert_values_equal(values, expected)

    def test_record_rule_value4(self):
        model_id = self._get_model_id()
        values = self.sec_mixin._auto_rule_values(self.env, model_id)[3]
        expected = {
            '_xmlid':
                '__auto__.cms_security_cms_security_mixin_'
                'allowed_groups_can_write_write_group_ids',
            'name':
                'cms_security_cms_security_mixin '
                'allowed groups can write (write_group_ids)',
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
                (4, self.env.ref('base.group_portal').id),
            ],
        }
        self._assert_values_equal(values, expected)
