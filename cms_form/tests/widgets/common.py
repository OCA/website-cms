# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo.tests.common import SavepointCase
import mock

from ..common import HTMLRenderMixin


def fake_form(**data):
    """Get a mocked fake form.

    :param data: kw args for setting form values
    """
    form = mock.MagicMock(name='FakeForm')
    form_values = mock.PropertyMock(return_value={'form_data': data})
    type(form).form_render_values = form_values
    return form


def fake_field(name, **kw):
    """Get fake field specs `form_fields` compliant.

    :param name: field name
    :param kw: kw args to override some values
    """
    info = {
        'type': 'char',
        'required': False,
        'string': name.capitalize().replace('_', ' '),
        'readonly': False,
        'help': 'Help for %s' % name,
    }
    info.update(kw)
    return name, info


def get_widget(env, fname, field, form=None, widget_model=None, **kw):
    """Retrieve and initialize widget.

    :param fname: field name
    :param field: field info matching `form_fields` schema
    :param form: an instance of a cms_form
    :param widget_model: if you don't pass a form you must pass a w model
    """
    assert form or widget_model
    if not form:
        form = fake_form()
    if not widget_model:
        widget_model = form.form_get_widget_model(fname, field)
    return env[widget_model].widget_init(
        form, fname, field, **kw
    )


class TestWidgetCase(SavepointCase, HTMLRenderMixin):

    at_install = False
    post_install = True

    @classmethod
    def get_widget(cls, fname, field, **kw):
        return get_widget(cls.env, fname, field, **kw)
