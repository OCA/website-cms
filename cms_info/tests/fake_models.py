# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class TestMixin(object):

    # generate xmlids
    # this is needed if you want to load data tied to a test model via xid
    _test_setup_gen_xid = False
    _test_teardown_no_delete = False

    @classmethod
    def _test_setup_model(cls, env):
        """Initialize it."""
        cls._build_model(env.registry, env.cr)
        env.registry.setup_models(env.cr)
        ctx = dict(env.context, update_custom_fields=True)
        if cls._test_setup_gen_xid:
            ctx['module'] = cls._module
        env.registry.init_models(env.cr, [cls._name], ctx)

    @classmethod
    def _test_teardown_model(cls, env):
        """Deinitialize it."""
        if not getattr(cls, '_test_teardown_no_delete', False):
            del env.registry.models[cls._name]
        env.registry.setup_models(env.cr)

    def _test_get_model_id(self):
        self.env.cr.execute(
            "SELECT id FROM ir_model WHERE model = %s", (self._name, ))
        res = self.env.cr.fetchone()
        return res[0] if res else None

    def _test_create_ACL(self, **kw):
        model_id = self._test_get_model_id()
        if not model_id:
            self._reflect()
            model_id = self._test_get_model_id()
        if model_id:
            vals = self._test_ACL_values(model_id)
            vals.update(kw)
            self.env['ir.model.access'].create(vals)

    def _test_ACL_values(self, model_id):
        values = {
            'name': 'Fake ACL for %s' % self._name,
            'model_id': model_id,
            'perm_read': 1,
            'perm_create': 1,
            'perm_write': 1,
            'perm_unlink': 1,
            'active': True,
        }
        return values


class FakeModel(models.Model, TestMixin):
    _name = 'fake.model'
    _inherit = 'website.published.mixin'
    _test_setup_ACL = True

    name = fields.Char()
