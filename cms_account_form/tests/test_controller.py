# Copyright 2018 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import odoo.tests.common as test_common
import mock
from ..controllers.account import MyAccount

MOD_PATH = 'odoo.addons.cms_account_form.controllers.account'


class TestController(test_common.SavepointCase):

    @mock.patch(MOD_PATH + '.request')
    def test_form_controller(self, mocked_req):
        type(mocked_req.env.user.partner_id).id = \
            mock.PropertyMock(return_value=10)
        ctrl = MyAccount()
        with mock.patch.object(ctrl, 'make_response') as mocked:
            ctrl.account()
            mocked.assert_called_once_with('res.partner', model_id=10)

        self.assertEqual(
            ctrl.form_model_key('res.partner'),
            'cms.form.my.account')
