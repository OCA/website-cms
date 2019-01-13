# Copyright 2019 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import json
from .common import TestWidgetCase, fake_form, fake_field


class TestWidgetX2M(TestWidgetCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partners = cls.env['res.partner'].search([], limit=4)
        cls.form = fake_form(
            # fake defaults
            # behavior of o2m or m2m ATM is the same
            m2m_field=cls.partners.ids[0:2],
        )

    def test_widget_x2many_base(self):
        w_name, w_field = fake_field(
            'm2m_field',
            type='many2many',
            relation='res.partner',
            domain=[('id', 'in', self.partners.ids)]
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.many2many')
        self.assertEqual(widget.w_comodel, self.env['res.partner'])
        self.assertEqual(widget.w_domain, [('id', 'in', self.partners.ids)])

    def test_widget_x2many(self):
        w_name, w_field = fake_field(
            'm2m_field',
            type='many2many',
            relation='res.partner',
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.many2many')
        expected_attrs = {
            'id': 'm2m_field',
            'name': 'm2m_field',
            'class': 'form-control js_select2_m2m_widget ',
            'placeholder': 'M2m field...',
            'data-init-value': json.dumps(self.partners.ids[0:2]),
            'data-model': 'res.partner',
            'data-domain': '[]',
            'data-fields': '["name"]',
        }
        self._test_widget_attributes(widget, 'input', expected_attrs)

    def test_widget_x2many_base_load(self):
        w_name, w_field = fake_field(
            'm2m_field',
            type='many2many',
            relation='res.partner',
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.many2many')
        # test conversion
        self.assertEqual(widget.w_load(m2m_field=False), '[]')
        self.assertEqual(
            widget.w_load(m2m_field='{},{}'.format(*self.partners.ids[0:2])),
            json.dumps(self.partners[0:2].read(['display_name', 'name'])),
        )

    def test_widget_x2many_base_load_from_record(self):
        categs = self.env['res.partner.category'].search([], limit=3)
        partner = self.partners[0]
        form = fake_form(
            # category_id=categs,
            main_object=partner,
        )
        w_name, w_field = fake_field(
            'category_id',
            type='many2many',
            relation=categs._name,
        )
        widget = self.get_widget(w_name, w_field, form=form,
                                 widget_model='cms.form.widget.many2many')
        # flush categories if any
        partner.category_id = False
        # flushed, no value
        self.assertEqual(widget.w_load(), '[]')
        # set some value
        partner.category_id = categs[0:2]
        # no value override from request: load from record
        self.assertEqual(
            widget.w_load(),
            json.dumps(partner.category_id.read(['display_name', 'name'])),
        )
        self.assertEqual(
            # pass new value via request
            widget.w_load(category_id=str(categs[-1].id)),
            json.dumps(categs[-1].read(['display_name', 'name'])),
        )

    def test_widget_x2many_base_extract(self):
        w_name, w_field = fake_field(
            'm2m_field',
            type='many2many',
            relation='res.partner',
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.many2many')
        # test conversion
        self.assertEqual(widget.w_extract(m2m_field='1,2,3'), [1, 2, 3])

    def test_widget_x2many_load_no_value(self):
        w_name, w_field = fake_field(
            'm2m_field',
            type='many2many',
            relation='res.partner',
        )
        widget = self.get_widget(w_name, w_field, form=self.form,
                                 widget_model='cms.form.widget.many2many')
        self.assertEqual(widget.w_load(m2m_field=''), '[]')
        # empty value from default_get
        self.assertEqual(widget.w_load(m2m_field=[(6, 0, [])]), '[]')
