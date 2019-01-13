# Copyright 2019 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import json
from .common import TestWidgetCase, fake_form, fake_field


class TestWidgetM2O(TestWidgetCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partners = cls.env['res.partner'].search([], limit=4)
        cls.form = fake_form(
            # fake defaults
            m2o_field=cls.partners.ids[0],
        )

    def test_widget_many2one_base(self):
        w_name, w_field = fake_field(
            'm2o_field',
            type='many2one',
            relation='res.partner',
            domain=[('id', 'in', self.partners.ids)]
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.many2one')
        self.assertEqual(widget.w_comodel, self.env['res.partner'])
        self.assertEqual(widget.w_domain, [('id', 'in', self.partners.ids)])
        self.assertEqual(
            widget.w_option_items, self.partners)

    def test_widget_many2one_base_load(self):
        # TODO: test load value from form record
        w_name, w_field = fake_field(
            'm2o_field',
            type='many2one',
            relation='res.partner',
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.many2one')

        self.assertEqual(widget.w_load(m2o_field='1'), 1)
        self.assertEqual(widget.w_load(m2o_field='0'), None)
        self.assertEqual(widget.w_load(m2o_field='a'), None)
        self.assertEqual(widget.w_load(m2o_field=1), 1)
        self.assertEqual(widget.w_load(
            m2o_field=self.partners[0]), self.partners[0].id)
        self.assertEqual(widget.w_load(m2o_field=''), None)
        self.assertEqual(widget.w_load(m2o_field=None), None)
        self.assertEqual(widget.w_load(m2o_field=False), False)

    def test_widget_many2one_base_extract(self):
        w_name, w_field = fake_field(
            'm2o_field',
            type='many2one',
            relation='res.partner',
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.many2one')

        self.assertEqual(widget.w_extract(m2o_field='1'), 1)
        self.assertEqual(widget.w_extract(m2o_field='0'), None)
        self.assertEqual(widget.w_extract(m2o_field='a'), None)
        self.assertEqual(widget.w_extract(m2o_field=1), 1)
        self.assertEqual(widget.w_extract(
            m2o_field=self.partners[0]), self.partners[0].id)
        self.assertEqual(widget.w_extract(m2o_field=''), None)
        # none to ignore any change
        self.assertEqual(widget.w_extract(m2o_field=None), None)
        # false to flush the field
        self.assertEqual(widget.w_extract(m2o_field=False), None)

    def test_widget_many2one_base_render(self):
        w_name, w_field = fake_field(
            'm2o_field',
            type='many2one',
            relation='res.partner',
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.many2one')
        expected_attrs = {
            'id': 'm2o_field',
            'name': 'm2o_field',
        }
        self._test_widget_attributes(widget, 'select', expected_attrs)
        widget.w_field['required'] = True
        expected_attrs['required'] = '1'
        self._test_widget_attributes(widget, 'select', expected_attrs)

    def test_widget_many2one_multi(self):
        w_name, w_field = fake_field(
            'm2o_field',
            type='many2one',
            relation='res.partner',
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.many2one.multi')
        expected_attrs = {
            'id': 'm2o_field',
            'name': 'm2o_field',
            'class': 'form-control js_select2_m2m_widget  m2o',
            'placeholder': 'M2o field...',
            'data-init-value': str(self.partners.ids[0]),
            'data-model': 'res.partner',
            'data-domain': '[]',
            'data-fields': '["name"]',
        }
        self._test_widget_attributes(widget, 'input', expected_attrs)

    def test_widget_many2one_multi_load(self):
        w_name, w_field = fake_field(
            'm2o_field',
            type='many2one',
            relation='res.partner',
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.many2one.multi')
        # test conversion
        self.assertEqual(widget.w_load(m2o_field=False), '[]')
        self.assertEqual(
            widget.w_load(m2o_field='{},{}'.format(*self.partners.ids[0:2])),
            json.dumps(self.partners[0:2].read(['name'])),
        )

    def test_widget_many2one_multi_extract(self):
        w_name, w_field = fake_field(
            'm2o_field',
            type='many2one',
            relation='res.partner',
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.many2one.multi')
        # test conversion
        self.assertEqual(widget.w_extract(m2o_field='1,2,3'), [1, 2, 3])
