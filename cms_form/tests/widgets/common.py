# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import SavepointCase
import mock


def fake_form():
    return mock.MagicMock(name='FakeForm')


def get_widget(env, fname, field, form=None, widget_model=None, **kw):
    """Retrieve and initialize widget.
    
    :param form: an instance of a cms_form
    :param fname: field name
    :param field: field info matching `form_fields` schema
    :param form: an instance of a cms_form
    :param widget_model: if you don't pass a form you must pass a w model
    """
    if not form:
        form = fake_form()
    if not widget_model:
        widget_model = form.form_get_widget_model(fname, field)
    return env[widget_model].widget_init(
        form, fname, field, **kw
    )


class TestWidgetCase(SavepointCase):

    at_install = False
    post_install = True

    def get_widget(self, fname, field, **kw):
        return get_widget(self.env, fname, field, **kw)
