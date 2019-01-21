# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class FakePartnerForm(models.AbstractModel):
    """A test model form."""

    _name = 'cms.form.res.partner'
    _inherit = 'cms.form'
    _form_model = 'res.partner'
    _form_model_fields = ('name', 'country_id')
    _form_required_fields = ('name', 'country_id')

    custom = fields.Char(default=lambda self: 'I am your default')

    def _form_load_custom(self, fname, field, value, **req_values):
        return req_values.get('custom', 'oh yeah!')


class FakePartnerFormProtectedFields(models.AbstractModel):
    """A test model form w/ `groups` protected fields."""

    _name = 'cms.form.protected.fields'
    _inherit = 'cms.form'
    # we'll test specifically that ordering won't break
    _form_fields_order = ['ihaveagroup', 'nogroup']

    nogroup = fields.Char()
    ihaveagroup = fields.Char(groups='website.group_website_designer')


class FakeSearchPartnerForm(models.AbstractModel):
    """A test model search form."""

    _name = 'cms.form.search.res.partner'
    _inherit = 'cms.form.search'
    _form_model = 'res.partner'
    _form_model_fields = ('name', 'country_id', )

    def form_search_domain(self, search_values):
        """Force domain to include only test-created records."""
        domain = super(
            FakeSearchPartnerForm, self
        ).form_search_domain(search_values)
        # we use this attr in tests to limit search results
        # to test records' scope
        include_only_ids = getattr(self, 'test_record_ids', [])
        if include_only_ids:
            domain.append(('id', 'in', include_only_ids))
        return domain


class FakeSearchPartnerFormMulti(models.AbstractModel):
    """A test model search form w/ multiple values for country."""

    _name = 'cms.form.search.res.partner.multicountry'
    _inherit = 'cms.form.search.res.partner'
    _form_search_fields_multi = ('country_id', )

    @property
    def form_widgets(self):
        res = super().form_widgets
        res.update({
            'country_id': 'cms.form.widget.many2one.multi',
        })
        return res


class FakePartnerChannelForm(models.AbstractModel):
    """A test model form."""

    _name = 'cms.form.mail.channel.partner'
    _inherit = 'cms.form'
    # This model has `_rec_name = 'partner_id'` and allows us
    # to test a specific case for form_title computation
    _form_model = 'mail.channel.partner'


class FakeFieldsForm(models.AbstractModel):
    """A test model form."""

    _name = 'cms.form.test_fields'
    _inherit = 'cms.form'

    a_char = fields.Char()
    a_number = fields.Integer()
    a_float = fields.Float()
    # fake relation fields
    a_many2one = fields.Char()
    a_one2many = fields.Char()
    a_many2many = fields.Char()

    def _form_fields(self):
        _fields = super()._form_fields()
        # fake fields' types
        _fields['a_many2one']['type'] = 'many2one'
        _fields['a_many2one']['relation'] = 'res.partner'
        _fields['a_many2many']['type'] = 'many2many'
        _fields['a_many2many']['relation'] = 'res.partner'
        _fields['a_one2many']['type'] = 'one2many'
        _fields['a_one2many']['relation'] = 'res.partner'
        return _fields

    def _form_validate_a_float(self, value, **request_values):
        """Specific validator for `a_float` field."""
        value = float(value or '0')
        return not value > 5, 'Must be greater than 5!'

    def _form_validate_char(self, value, **request_values):
        """Specific validator for all `char` fields."""
        return not len(value) > 8, 'Text length must be greater than 8!'


class FakeFieldsFormWithFieldsets(models.AbstractModel):
    """A test model form."""

    _name = 'cms.form.test_fieldsets'
    _inherit = 'cms.form.test_fields'
    _form_fieldsets = [
        {
            'id': 'main',
            'fields': ['a_char', ],
        },
        {
            'id': 'numbers',
            'title': 'Number fields',
            'description': 'Only number fields here',
            'fields': ['a_number', 'a_float'],
            'css_extra_klass': 'best_fieldset',
        },
        {
            'id': 'relations',
            'title': 'Only relations here',
            'fields': ['a_many2one', 'a_many2many', 'a_one2many'],
        },
        {
            'id': 'protected',
            'fields': ['ihaveagroup'],
        },
    ]
    ihaveagroup = fields.Char(groups='website.group_website_designer')


FAKE_STORAGE = {}


class FakeWiz(models.AbstractModel):
    """A wizard form."""

    _name = 'fake.wiz'
    _inherit = 'cms.form.wizard'
    _wiz_name = _name

    def form_check_permission(self, raise_exception=True):
        # no need for this
        pass

    @property
    def _wiz_storage(self):
        return FAKE_STORAGE

    def wiz_configure_steps(self):
        return {
            1: {'form_model': 'fake.wiz.step1.country'},
            2: {'form_model': 'fake.wiz.step2.partner'},
            3: {'form_model': 'fake.wiz.step3.partner'},
        }


class FakeWizStep1Country(models.AbstractModel):

    _name = 'fake.wiz.step1.country'
    _inherit = 'fake.wiz'
    _form_model = 'res.country'
    _form_model_fields = ('name', )


class FakeWizStep2Partner(models.AbstractModel):

    _name = 'fake.wiz.step2.partner'
    _inherit = 'fake.wiz'
    _form_model = 'res.partner'
    _form_model_fields = ('name', 'to_be_stored', )
    _wiz_step_stored_fields = ('to_be_stored', )

    to_be_stored = fields.Char()


class FakeWizStep3Partner(models.AbstractModel):

    _name = 'fake.wiz.step3.partner'
    _inherit = 'fake.wiz'
    _form_model = 'res.partner'
    _form_model_fields = ('name', )


WIZ_KLASSES = [
    FakeWiz, FakeWizStep1Country,
    FakeWizStep2Partner, FakeWizStep3Partner
]


# `AbstractModel` or `TransientModel` needed to make ACL check happy`
class FakePubModel(models.TransientModel):
    _name = 'fake.publishable'
    _inherit = [
        'website.published.mixin',
    ]
    name = fields.Char()

    def _compute_website_url(self):
        for item in self:
            item.website_url = '/publishable/%d' % item.id


class FakePubModelForm(models.AbstractModel):
    _name = 'cms.form.fake.publishable'
    _inherit = 'cms.form'
    _form_model = 'fake.publishable'
    _form_model_fields = ('name', )


# `AbstractModel` or `TransientModel` needed to make ACL check happy`
class FakeNonPubModel(models.TransientModel):
    _name = 'fake.non.publishable'
    name = fields.Char()


class FakeNonPubModelForm(models.AbstractModel):
    _name = 'cms.form.fake.non.publishable'
    _inherit = 'cms.form'
    _form_model = 'fake.non.publishable'
    _form_model_fields = ('name', )
