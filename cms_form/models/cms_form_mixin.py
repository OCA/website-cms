# -*- coding: utf-8 -*-
# Copyright 2016 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models
from ..utils import DEFAULT_LOADERS, DEFAULT_EXTRACTORS
from ..import widgets

import inspect
import types
import werkzeug
from collections import OrderedDict


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
        'store', 'help',
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
        return self.__form_main_object

    @main_object.setter
    def main_object(self, value):
        self.__form_main_object = value

    def form_init(self, request, main_object=None, **kw):
        """Initalize a form instance.

        @param request: an odoo-wrapped werkeug request
        @param main_object: current model instance if any
        @param kw: pass any override for `_form_` attributes
            ie: `fields_attributes` -> `_form_fields_attributes`
        """
        self.o_request = request  # odoo wrapped request
        self.request = request.httprequest  # werkzeug request, the "real" one
        self.main_object = main_object
        # override `_form_` parameters
        for k, v in kw.iteritems():
            if not inspect.ismethod(getattr(self, '_form_' + k)):
                setattr(self, '_form_' + k, v)

    # internal flag for successful form
    __form_success = False

    @property
    def form_success(self):
        return self.__form_success

    @form_success.setter
    def form_success(self, value):
        self.__form_success = value

    @property
    def form_title(self):
        return ''

    @property
    def form_description(self):
        return ''

    @property
    def form_mode(self):
        if self._form_mode:
            return self._form_mode
        if self.request.method.upper() == 'GET':
            return 'read'
        elif self.request.method.upper() == 'POST':
            if self.main_object:
                return 'write'
            return 'create'
        return 'base'

    @property
    def form_model(self):
        return self.env[self._form_model]

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
        self._remove_unwanted(_all_fields)
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

    def _remove_unwanted(self, _all_fields):
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
        # normal fields
        values = {
            k: v for k, v in self.request.args.iteritems()
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
            # 1nd lookup for a default type / name handler
            value_handler = self._form_loaders.get(
                field['type'], self._form_loaders.get(fname, None))
            if value_handler:
                value = value_handler(
                    self, main_object, fname, value, **request_values)
            # 2nd lookup for a specific type handler
            value_handler = getattr(
                self, '_form_load_' + field['type'], value_handler)
            # 3rd lookup and override by named handler if any
            value_handler = getattr(
                self, '_form_load_' + fname, value_handler)
            if value_handler and isinstance(value_handler, types.MethodType):
                value = value_handler(
                    main_object, fname, value, **request_values)
            defaults[fname] = value
        if main_object:
            # TODO: still needed?
            # add `has_*` flags for file fields
            # so in templates we really know if a file field is valued.
            for fname in self.form_file_fields.iterkeys():
                defaults['has_' + fname] = bool(main_object[fname])
        return defaults

    def form_extract_values(self, **request_values):
        """Extract values from request form."""
        request_values = request_values or self.form_get_request_values()
        values = {}
        for fname, field in self.form_fields().iteritems():
            value = request_values.get(fname)
            # 1nd lookup for a default type or name handler
            value_handler = self._form_extractors.get(
                field['type'], self._form_extractors.get(fname, None))
            # 2nd lookup for a specific type handler
            value_handler = getattr(
                self, '_form_extract_' + field['type'], value_handler)
            # 3rd lookup and override by named handler if any
            value_handler = getattr(
                self, '_form_extract_' + fname, value_handler)
            if value_handler:
                value = value_handler(self, fname, value, **request_values)
            if value is None:
                # we assume we do not want to override the field value.
                # a tipical example is an image field.
                # If you have an existing image
                # you cannot set the default value on the file input
                # for standard HTML security restrictions.
                # If you want to flush a value on a field just return "False".
                continue
            values[fname] = value
        return values

    __form_render_values = {}

    @property
    def form_render_values(self):
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
        values = self.form_render_values.copy()
        values.update(kw)
        return self.env.ref(self.form_template).render(values)

    def form_process(self, **kw):
        render_values = self.form_render_values
        render_values.update(kw)
        render_values['form_data'] = self.form_load_defaults()
        handler = getattr(self, 'form_process_' + self.request.method.upper())
        render_values.update(handler(render_values))
        self.form_render_values = render_values

    def form_process_GET(self, render_values):
        return render_values

    @property
    def form_wrapper_css_klass(self):
        return ' '.join([
            'cms_form_wrapper',
            self._form_model.replace('.', '_').lower(),
            self._form_wrapper_extra_css_klass,
            'mode_' + self.form_mode,
        ])

    @property
    def form_css_klass(self):
        return self._form_extra_css_klass

    def form_check_empty_field(self, fname, field, value, **req_values):
        if isinstance(value, werkzeug.datastructures.FileStorage):
            has_value = bool(value.filename)
            if not has_value and req_values.get(fname + '_keepcheck') == 'yes':
                # no value, but we want to preserve existing one
                return False
            # file field w/ no content
            # TODO: this is not working sometime...
            # return not bool(value.content_length)
            return not has_value
        return value in (False, '')
