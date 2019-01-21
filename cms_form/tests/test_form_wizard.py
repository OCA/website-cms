# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from .common import FormSessionTestCase
from .utils import fake_request
from .fake_models import (
    FakeWiz, FakeWizStep1Country,
    FakeWizStep2Partner, FakeWizStep3Partner,
    FAKE_STORAGE,
)


class TestCMSFormWizard(FormSessionTestCase):

    TEST_MODELS_KLASSES = (
        FakeWiz, FakeWizStep1Country,
        FakeWizStep2Partner, FakeWizStep3Partner,
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_models()

    @classmethod
    def tearDownClass(cls):
        cls._teardown_models()
        super().tearDownClass()

    def tearDown(self):
        FAKE_STORAGE.clear()
        super().tearDown()

    def test_wiz_base_attrs(self):
        form = self.get_form(FakeWizStep1Country._name)
        # check wrapper class override
        self.assertEqual(
            form.form_wrapper_css_klass,
            # wrapper klass, normalized wizard step model
            'cms_form_wrapper fake_wiz_step1_country '
            # normalized model, mode, normalized wizard model
            'res_country mode_wizard fake_wiz'
        )
        # check default storage key
        self.assertEqual(form._wiz_storage_key, 'fake.wiz')
        # check default storage
        self.assertEqual(
            form._wiz_storage, {
                'fake.wiz': {
                    'steps': {1: {}, 2: {}, 3: {}},
                    'current': 1,
                    'next': 2,
                    'prev': None
                }
            }
        )
        self.assertEqual(form.wiz_steps, [1, 2, 3])

    def test_wiz_use_session_by_default(self):
        req = fake_request(session=self.session)
        form = self.get_form('cms.form.wizard', req=req)
        self.assertEqual(
            form._wiz_storage.__class__.__name__, 'OpenERPSession')

    def test_wiz_configure_steps(self):
        form = self.get_form('cms.form.wizard')
        self.assertEqual(form.wiz_configure_steps(), {})

    def test_wiz_step_info(self):
        form = self.get_form(FakeWizStep1Country._name)
        with self.assertRaises(ValueError) as err:
            form.wiz_get_step_info(100)
        self.assertEqual(str(err.exception), 'Step `100` does not exists.')
        self.assertEqual(
            form.wiz_get_step_info(1), {'form_model': 'fake.wiz.step1.country'}
        )
        self.assertEqual(
            form.wiz_get_step_info(2), {'form_model': 'fake.wiz.step2.partner'}
        )
        self.assertEqual(
            form.wiz_get_step_info(3), {'form_model': 'fake.wiz.step3.partner'}
        )

    def test_wiz_save_step(self):
        form = self.get_form(FakeWizStep1Country._name)
        # no step passed, use current one (1)
        form.wiz_save_step({'foo': 'baz'})
        self.assertEqual(form.wiz_load_step(1), {'foo': 'baz'})
        form.wiz_save_step({'boo': 'waz'}, step=3)
        self.assertEqual(form.wiz_load_step(3), {'boo': 'waz'})
        # corner case whereas a step in the storage has been removed
        form.wiz_storage_get()['steps'].pop(2)
        form.wiz_save_step({'get': 'back'}, step=2)
        self.assertEqual(form.wiz_load_step(2), {'get': 'back'})

    def test_wiz_init(self):
        form = self.get_form(FakeWizStep1Country._name)
        self.assertEqual(form.wiz_storage_get()['current'], 1)
        self.assertEqual(form.wiz_storage_get()['next'], 2)
        self.assertEqual(form.wiz_storage_get()['prev'], None)
        self.assertEqual(len(form.wiz_storage_get()['steps']), 3)

    def test_wiz_init_from_another_page(self):
        form = self.get_form(FakeWizStep1Country._name, page=2)
        self.assertEqual(form.wiz_storage_get()['current'], 2)
        self.assertEqual(form.wiz_storage_get()['next'], 3)
        self.assertEqual(form.wiz_storage_get()['prev'], 1)

    def test_wiz_next_prev1(self):
        form = self.get_form(FakeWizStep1Country._name)
        self.assertEqual(form.wiz_prev_step(), None)
        self.assertEqual(form.wiz_current_step(), 1)
        self.assertEqual(form.wiz_next_step(), 2)

    def test_wiz_next_prev2(self):
        form = self.get_form(FakeWizStep2Partner._name, page=2)
        self.assertEqual(form.wiz_prev_step(), 1)
        self.assertEqual(form.wiz_current_step(), 2)
        self.assertEqual(form.wiz_next_step(), 3)

    def test_wiz_next_prev3(self):
        form = self.get_form(FakeWizStep3Partner._name, page=3)
        self.assertEqual(form.wiz_prev_step(), 2)
        self.assertEqual(form.wiz_current_step(), 3)
        self.assertEqual(form.wiz_next_step(), None)

    def test_wiz_next_prev_url1(self):
        form = self.get_form(FakeWizStep1Country._name)
        self.assertEqual(
            form.form_next_url(), '/cms/wiz/fake.wiz/page/2')
        # simulate click on prev button
        req = fake_request(form_data={'wiz_submit': 'prev'}, method='POST')
        form = self.get_form(FakeWizStep1Country._name, req=req)
        # when step is none we default to initial one
        self.assertEqual(form.form_next_url(), '/cms/wiz/fake.wiz/page/1')

    def test_wiz_next_prev_url2(self):
        form = self.get_form(FakeWizStep2Partner._name, page=2)
        self.assertEqual(
            form.form_next_url(), '/cms/wiz/fake.wiz/page/3')
        req = fake_request(form_data={'wiz_submit': 'prev'}, method='POST')
        form = self.get_form(FakeWizStep2Partner._name, page=2, req=req)
        self.assertEqual(
            form.form_next_url(), '/cms/wiz/fake.wiz/page/1')

    def test_wiz_next_prev_url3(self):
        form = self.get_form(FakeWizStep3Partner._name, page=3)
        # 3 it's the last step so next url defaults to initial one
        self.assertEqual(form.form_next_url(), '/cms/wiz/fake.wiz/page/1')
        req = fake_request(form_data={'wiz_submit': 'prev'}, method='POST')
        form = self.get_form(FakeWizStep2Partner._name, page=3, req=req)
        self.assertEqual(
            form.form_next_url(), '/cms/wiz/fake.wiz/page/2')

    def test_wiz_stored_fields(self):
        data = {
            'name': 'John Doe',
            'to_be_stored': 'Whatever',
        }
        req = fake_request(form_data=data, method='POST')
        form = self.get_form(FakeWizStep2Partner._name, req=req)
        main_object = form.form_create_or_update()
        self.assertEqual(main_object.name, 'John Doe')
        step_values = form.wiz_load_step()
        self.assertDictEqual(step_values, {'to_be_stored': 'Whatever'})

    def test_wiz_stored_fields_all(self):
        data = {
            'name': 'John Doe',
            'to_be_stored': 'Whatever',
        }
        req = fake_request(form_data=data, method='POST')
        form = self.get_form(FakeWizStep2Partner._name, req=req)
        form._wiz_step_stored_fields = 'all'
        main_object = form.form_create_or_update()
        self.assertEqual(main_object.name, 'John Doe')
        step_values = form.wiz_load_step()
        self.assertDictEqual(step_values, {
            'name': 'John Doe',
            'to_be_stored': 'Whatever',
        })
