# -*- coding: utf-8 -*-

from openerp.tests import common


@common.at_install(False)
@common.post_install(True)
class TestPage(common.TransactionCase):

    at_install = False
    post_install = True

    def setUp(self):
        super(TestPage, self).setUp()
        self.model = self.env['cms.page']
        self.news_type = self.env.ref('cms_page.page_type_news')
        self.view2 = self.env.ref('cms_page.page_default_with_description')

    def test_page_default_values(self):
        page = self.model.create({'name': 'foo'})
        page.sub_page_type_id = self.news_type
        page.sub_page_view_id = self.view2

        sub = page.with_context(
            page._child_create_context()).create({'name': 'Sub'})
        self.assertEqual(self.news_type, sub.type_id)
        self.assertEqual(self.view2, sub.view_id)
