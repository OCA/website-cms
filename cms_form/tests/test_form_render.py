# -*- coding: utf-8 -*-
# Copyright 2016 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# from .common import fake_request
from .common import FormTestCase


class TestRender(FormTestCase):

    def test_render(self):
        form = self.get_form('cms.form.test_fields')
        html = form.form_render()
        # TODO: test with html parsing
        self.assertTrue('<form' in html)
