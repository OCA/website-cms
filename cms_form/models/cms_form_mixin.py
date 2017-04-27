# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import inspect
import json
from collections import OrderedDict

from openerp import models

from .. import widgets
from ..utils import DEFAULT_LOADERS, DEFAULT_EXTRACTORS, data_merge


IGNORED_FORM_FIELDS = [
    'display_name',
    '__last_update',
    # TODO: retrieve from inherited schema
    'message_ids',
    'message_follower_ids',
    'message_follower',
    'message_last_post',
    'message_unread',
    'message_unread_counter',
    'message_needaction_counter',
    'website_message_ids',
    'website_published',
] + models.MAGIC_COLUMNS


class CMSFormMixin(models.AbstractModel):
    """Base abstract CMS form."""
    _name = 'cms.form.mixin'
    _description = 'CMS Form mixin'

    # template to render the form
    form_template = 'cms_form.base_form'
    form_fields_template = 'cms_form.base_form_fields'
    form_buttons_template = 'cms_form.base_form_buttons'
    form_action = ''
    form_method = 'POST'
    _form_mode = ''
    # extra css klasses for the whole form wrapper
    _form_wrapper_extra_css_klass = ''
    # extra css klasses for just the form element
    _form_extra_css_klass = ''
    _form_widgets = widgets.DEFAULT_WIDGETS
    # model tied to this form
    _form_model = ''
    # model's fields to load
    _form_model_fields = []
    # force fields order
    _form_fields_order = []
    # quickly force required fields
    _form_required_fields = ()
    # fields' attributes to load
    _form_fields_attributes = [
        'type', 'string', 'domain',
        'required', 'readonly', 'relation',
        'store', 'help', 'selection',
    ]
    # include only these fields
    _form_fields_whitelist = ()
    # exclude these fields
    _form_fields_blacklist = ()
    # handlers to load values from existing item or simple defaults
    _form_loaders = DEFAULT_LOADERS
    # handlers to extract values from request
    _form_extractors = DEFAULT_EXTRACTORS
    # extract values mode
    # This param can be used to alter value format
    # when extracting values from request.
    # eg: in write mode you can get on a m2m [(6, 0, [1,2,3])]
    # while in read mode you can get just the ids [1,2,3]
    _form_extract_value_mode = 'write'
    # ignore this fields default
    __form_fields_ignore = IGNORED_FORM_FIELDS
    # current edit object if any
    __form_main_object = None

    @property
    def main_object(self):
        """Current main object."""
        return self.__form_main_object

    @main_object.setter
    def main_object(self, value):
        """Current main object setter."""
        self.__form_main_object = value

    def form_init(self, request, main_object=None, **kw):
        """Initalize a form instance.

        @param request: an odoo-wrapped werkeug request
        @param main_object: current model instance if any
        @param kw: pass any override for `_form_` attributes
            ie: `fields_attributes` -> `_form_fields_attributes`
        """
        form = self.new()
        form.o_request = request  # odoo wrapped request
        form.request = request.httprequest  # werkzeug request, the "real" one
        form.main_object = main_object
        # override `_form_` parameters
        for k, v in kw.iteritems():
            if not inspect.ismethod(getattr(form, '_form_' + k)):
                setattr(form, '_form_' + k, v)
        return form

    @property
    def form_title(self):
        return ''

    @property
    def form_description(self):
        return ''

    @property
    def form_mode(self):
        if self._form_mode:
            # forced mode
            return self._form_mode
        if self.main_object:
            return 'edit'
        return 'create'

    @property
    def form_model(self):
        return self.env[self._form_model]

    # TODO: cache fields per form instance?
    # if we do it we must take into account
    # some fields attributes (like widgets)
    # that may vary on a per-request base.
    def form_fields(self):
        """Retrieve form fields ready to be used.

        Fields lookup:
        * model's fields
        * form's fields

        Blacklisted fields are skipped.
        Whitelisted fields are loaded only.
        """
        _all_fields = OrderedDict()
        # load model fields
        _model_fields = {}
        if self._form_model:
            _model_fields = self.form_model.fields_get(
                self._form_model_fields,
                attributes=self._form_fields_attributes)
        # load form fields
        _form_fields = self.fields_get(attributes=self._form_fields_attributes)
        _all_fields.update(_model_fields)
        # form fields override model fields
        _all_fields.update(_form_fields)
        # exclude blacklisted
        for fname in self._form_fields_blacklist:
            # make it fail if passing wrong field name
            _all_fields.pop(fname)
        # include whitelisted
        _all_whitelisted = {}
        for fname in self._form_fields_whitelist:
            _all_whitelisted[fname] = _all_fields[fname]
        _all_fields = _all_whitelisted or _all_fields
        # remove unwanted fields
        self._form_remove_uwanted(_all_fields)
        # remove non-stored fields to exclude computed
        _all_fields = {k: v for k, v in _all_fields.iteritems() if v['store']}
        # update fields attributes
        self.form_update_fields_attributes(_all_fields)
        # update fields order
        if self._form_fields_order:
            _sorted_all_fields = OrderedDict()
            for fname in self._form_fields_order:
                _sorted_all_fields[fname] = _all_fields[fname]
            _all_fields = _sorted_all_fields
        return _all_fields

    def _form_remove_uwanted(self, _all_fields):
        """Remove fields from form fields."""
        for fname in self.__form_fields_ignore:
            _all_fields.pop(fname, None)

    def form_update_fields_attributes(self, _fields):
        """Manipulate fields attributes."""
        for fname, field in _fields.iteritems():
            if fname in self._form_required_fields:
                _fields[fname]['required'] = True
            field['widget'] = widgets.CharWidget(self, fname, field)
            for key in (field['type'], fname):
                if key in self._form_widgets:
                    widget = self._form_widgets[key]
                    field['widget'] = widget(self, fname, field)

    @property
    def form_file_fields(self):
        """File fields."""
        return {
            k: v for k, v in self.form_fields().iteritems()
            if v['type'] == 'binary'
        }

    def form_get_request_values(self):
        """Retrieve fields values from current request."""
        # on POST requests values are in `form` attr
        # on GET requests values are in `args` attr
        _values = self.request.form
        if not _values:
            # make sure to give precedence to form attribute
            # since you might get some extra params (like ?redirect)
            # and this will make the form machinery miss all the fields
            _values = self.request.args
        # normal fields
        values = {
            k: v for k, v in _values.iteritems()
            if k not in ('csrf_token', )
        }
        # file fields
        values.update(
            {k: v for k, v in self.request.files.iteritems()}
        )
        return values

    def form_load_defaults(self, main_object=None, request_values=None):
        """Load default values.

        Values lookup order:

        1. `main_object` fields' values (if an existing main_object is passed)
        2. request parameters (only parameters matching form fields names)
        """
        main_object = main_object or self.main_object
        request_values = request_values or self.form_get_request_values()
        defaults = request_values.copy()
        form_fields = self.form_fields()
        for fname, field in form_fields.iteritems():
            value = None
            # we could have form-only fields (like `custom` in test form below)
            if main_object and fname in main_object:
                value = main_object[fname]
            # maybe a POST request with new values: override item value
            value = request_values.get(fname, value)
            loader = self.form_get_loader(
                fname, field,
                main_object=main_object, value=value, **request_values)
            if loader:
                value = loader(
                    self, main_object, fname, value, **request_values)
            defaults[fname] = value
        return defaults

    def form_get_loader(self, fname, field,
                        main_object=None, value=None, **req_values):
        """Retrieve form value loader.

        :param fname: field name
        :param field: field description as `fields_get`
        :param main_object: current main object if any
        :param value: current field value if any
        :param req_values: custom request valuess
        """
        # 1nd lookup for a default type / name loader
        loader = self._form_loaders.get(
            field['type'], self._form_loaders.get(fname, None))
        if loader:
            value = loader(
                self, main_object, fname, value, **req_values)
        # 2nd lookup for a specific type loader method
        loader = getattr(
            self, '_form_load_' + field['type'], loader)
        # 3rd lookup and override by named loader if any
        loader = getattr(
            self, '_form_load_' + fname, loader)
        return loader

    def form_extract_values(self, **request_values):
        """Extract values from request form."""
        request_values = request_values or self.form_get_request_values()
        values = {}
        for fname, field in self.form_fields().iteritems():
            value = request_values.get(fname)
            extractor = self.form_get_extractor(
                fname, field, value=value, **request_values)
            if extractor:
                value = extractor(self, fname, value, **request_values)
            if value is None:
                # we assume we do not want to override the field value.
                # a typical example is an image field.
                # If you have an existing image
                # you cannot set the default value on the file input
                # for standard HTML security restrictions.
                # If you want to flush a value on a field just return "False".
                continue
            values[fname] = value
        return values

    def form_get_extractor(self, fname, field, value=None, **req_values):
        """Retrieve form value extractor.

        :param fname: field name
        :param field: field description as `fields_get`
        :param value: current field value if any
        :param req_values: custom request valuess
        """
        # 1nd lookup for a default type or name handler
        extractor = self._form_extractors.get(
            field['type'], self._form_extractors.get(fname, None))
        # 2nd lookup for a specific type handler
        extractor = getattr(
            self, '_form_extract_' + field['type'], extractor)
        # 3rd lookup and override by named handler if any
        extractor = getattr(
            self, '_form_extract_' + fname, extractor)
        return extractor

    __form_render_values = {}

    @property
    def form_render_values(self):
        """Values used to render the form."""
        if not self.__form_render_values:
            # default render values
            self.__form_render_values = {
                'main_object': self.main_object,
                'form': self,
                'form_data': {},
                'errors': {},
                'errors_messages': {},
            }
        return self.__form_render_values

    @form_render_values.setter
    def form_render_values(self, value):
        self.__form_render_values = value

    def form_render(self, **kw):
        """Renders form template declared in `form_template`.

        To render the form simply do:

            <t t-raw="form.form_render()" />
        """
        values = self.form_render_values.copy()
        values.update(kw)
        return self.env.ref(self.form_template).render(values)

    def form_process(self, **kw):
        """Process current request.

        :param kw: inject custom / extra rendering values.

        Lookup correct request handler by request method
        and call it with rendering values.
        The handler can perform any action (like creating objects)
        and then return final rendering form values
        and store them into `form_render_values`.
        """
        render_values = self.form_render_values
        render_values.update(kw)
        render_values['form_data'] = self.form_load_defaults()
        handler = getattr(self, 'form_process_' + self.request.method.upper())
        render_values.update(handler(render_values))
        self.form_render_values = render_values

    def form_process_GET(self, render_values):
        """Process GET requests."""
        return render_values

    def form_process_POST(self, render_values):
        """Process POST requests."""
        raise NotImplementedError()

    @property
    def form_wrapper_css_klass(self):
        """Return form wrapper css klass.

        By default the form markup is wrapped
        into a `cms_form_wrapper` element.
        You can use this set of klasses to customize form styles.

        Included by default:
        * `cms_form_wrapper` marker
        * form model name normalized (res.partner -> res_partner)
        * `_form_wrapper_extra_css_klass` extra klasses from form attribute
        * `mode_` + form mode (ie: 'mode_write')
        """
        parts = [
            'cms_form_wrapper',
            self._form_model.replace('.', '_').lower(),
            self._form_wrapper_extra_css_klass,
            'mode_' + self.form_mode,
        ]
        return ' '.join([x.strip() for x in parts if x.strip()])

    @property
    def form_css_klass(self):
        """Return `<form />` element css klasses.

        By default you can provide extra klasses via `_form_extra_css_klass`.
        """
        return self._form_extra_css_klass

    def form_json_info(self):
        info = {}
        info.update({
            'master_slave': self._form_master_slave_info()
        })
        return json.dumps(info)

    def _form_master_slave_info(self):
        """Return info about master/slave fields JSON compatible.

        # TODO: support pyeval expressions in JS

        Eg: {
            'field_master1': {
                'hide': {
                    # field to hide: values
                    # TODO: support pyeval expressions
                    'field_slave1': (master_value1, ),
                },
                'show': {
                    # field to show: pyeval expr
                    'field_slave1': (master_value2, ),
                },
            }
        }
        """
        return {}

    def _form_info_merge(self, info, tomerge):
        """Merge info dictionaries.

        Practical example:
        when inheriting forms you can add extra rules for the same master field
        so if you don't want to override info completely
        you can use this method to merge them properly.
        """
        return data_merge(info, tomerge)
