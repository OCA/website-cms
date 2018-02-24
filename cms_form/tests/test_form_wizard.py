# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from .common import FormSessionTestCase
from .utils import fake_request
from .fake_models import (
    FakeWiz, FakeWizStep1Country,
    FakeWizStep2Partner, FakeWizStep3Partner,
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

    def test_wiz_init(self):
        form = self.get_form(FakeWizStep1Country._name)
        self.assertEqual(form.wiz_storage_get()['current'], 1)
        self.assertEqual(form.wiz_storage_get()['next'], 2)
        self.assertEqual(form.wiz_storage_get()['prev'], None)
        self.assertEqual(len(form.wiz_storage_get()['steps']), 3)

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
