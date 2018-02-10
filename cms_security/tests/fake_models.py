# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import models, fields


class FakeSecuredModel(models.Model):
    """A test model that implements `cms.security.mixin`."""

    _name = 'fakemodel.secured'
    _description = 'cms_mixin: secured test model'
    _inherit = [
        'website.published.mixin',
        'cms.security.mixin',
    ]
    # generate security automatically
    _cms_auto_security_policy = True

    name = fields.Char()
    # test attachment deletion too
    image = fields.Binary(attachment=True)


def setup_test_model(env, model_cls):
    """Pass a test model class and initialize it.

    Courtesy of SBidoul from https://github.com/OCA/mis-builder :)
    """
    model_cls._build_model(env.registry, env.cr)
    env.registry.setup_models(env.cr)
    env.registry.init_models(
        env.cr, [model_cls._name],
        dict(env.context, update_custom_fields=True)
    )


def teardown_test_model(env, model_cls):
    """Pass a test model class and deinitialize it.

    Courtesy of SBidoul from https://github.com/OCA/mis-builder :)
    """
    if not getattr(model_cls, '_teardown_no_delete', False):
        del env.registry.models[model_cls._name]
    env.registry.setup_models(env.cr)
