# Copyright 2018 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import odoo.tests.common as test_common
import mock
from ..controllers import main as controllers

MOD_PATH = 'odoo.addons.cms_notification.controllers.main'


class TestController(test_common.SavepointCase):

    @mock.patch(MOD_PATH + '.http')
    def test_panel_form_controller(self, mocked_http):
        type(mocked_http.request.env.user).id = \
            mock.PropertyMock(return_value=10)
        ctrl = controllers.PanelFormController()
        with mock.patch.object(ctrl, 'make_response') as mocked:
            ctrl.cms_form()
            mocked.assert_called_once_with('res.users', model_id=10)

        self.assertEqual(ctrl.form_model_key('res.users'),
                         'cms.notification.panel.form')

    @mock.patch(MOD_PATH + '.http')
    def test_my_notif_controller(self, mocked_http):
        type(mocked_http.request.env.user).id = \
            mock.PropertyMock(return_value=20)
        ctrl = controllers.MyNotificationsController()
        with mock.patch.object(ctrl, 'make_response') as mocked:
            ctrl.cms_form()
            mocked.assert_called_once_with('res.users', model_id=20)

        self.assertEqual(ctrl.form_model_key('res.users'),
                         'cms.notification.listing')
