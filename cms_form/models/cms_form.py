# -*- coding: utf-8 -*-
# Copyright 2016 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models
from openerp import _
from openerp.tools.mimetypes import guess_mimetype

import json
import inspect
import base64
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


def m2o_to_form(form, record, fname, value, **req_values):
    # important: return False if no value
    # otherwise you will compare an empty recordset with an id
    # in a select input in form widget template.
    if isinstance(value, basestring) and value.isdigit():
        # number as string
        return int(value)
    elif isinstance(value, models.BaseModel):
        return value and value.id or None
    return None


def x2many_to_form(form, record, fname, value,
                   display_field='display_name', **req_values):
    value = [{'id': x.id, 'name': x[display_field]} for x in value or []]
    value = json.dumps(value)
    return value


def binary_to_form(form, record, fname, value, **req_values):
    _value = {
        # 'value': '',
        # 'raw_value': '',
        # 'mimetype': '',
    }
    if value:
        mimetype = guess_mimetype(value.decode('base64'))
        _value = {
            'value': value,
            'raw_value': value,
            'mimetype': mimetype,
        }
        if mimetype.startswith('image/'):
            _value['value'] = 'data:{};base64,{}'.format(mimetype, value)
    return _value


def form_to_integer(form, fname, value, **req_values):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def form_to_float(form, fname, value, **req_values):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def form_to_x2many(form, fname, value, **req_values):
    _value = False
    if value:
        ids = [int(rec_id) for rec_id in value.split(',')]
        _value = [(6, False, ids)]
    return _value


def form_to_binary(form, fname, value, **req_values):
    _value = False
    if req_values.get(fname + '_keepcheck') == 'yes':
        # prevent discarding image
        req_values.pop(fname, None)
        req_values.pop(fname + '_keepcheck')
        return None
    if value:
        if hasattr(value, 'read'):
            file_content = value.read()
            _value = base64.encodestring(file_content)
        else:
            _value = value.split(',')[-1]
    return _value


def form_to_date(form, fname, value, **req_values):
    if not value:
        # make sure we do not return empty string which breaks the ORM
        return False
    return value


DEFAULT_LOADERS = {
    'many2one': m2o_to_form,
    'one2many': x2many_to_form,
    'many2many': x2many_to_form,
    'binary': binary_to_form,
}
DEFAULT_EXTRACTORS = {
    'integer': form_to_integer,
    'float': form_to_float,
    'many2one': form_to_integer,
    'one2many': form_to_x2many,
    'many2many': form_to_x2many,
    'binary': form_to_binary,
    'date': form_to_date,
    'datetime': form_to_date,
}


class CMSFormMixin(models.AbstractModel):
    """Base abstract CMS form."""
    _name = 'cms.form.mixin'
    _description = 'CMS Form mixin'

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
    # handlers to extract values from request
    _form_extractors = DEFAULT_EXTRACTORS
    # handlers to load values from existing item or simple defaults
    _form_loaders = DEFAULT_LOADERS
    # ignore this fields default
    __form_fields_ignore = IGNORED_FORM_FIELDS
    # internal flag for successful form
    __form_success = False

    def form_init(self, request, main_object=None, **kw):
        """Initalize a form instance.

        @param request: an odoo-wrapped werkeug request
        @parm kw: pass any override for `_form_` attributes
            ie: `fields_attributes` -> `_form_fields_attributes`
        """
        self.o_request = request  # odoo wrapped request
        self.request = request.httprequest  # werkzeug request, the "real" one
        self.main_object = main_object
        # override `_form_` parameters
        for k, v in kw.iteritems():
            if not inspect.ismethod(getattr(self, '_form_' + k)):
                setattr(self, '_form_' + k, v)

    @property
    def form_success(self):
        return self.__form_success

    @form_success.setter
    def form_success(self, value):
        self.__form_success = value

    @property
    def form_title(self):
        # TODO
        return 'Form title'

    @property
    def form_description(self):
        # TODO
        return 'Form description'

    @property
    def form_mode(self):
        if self._form_mode:
            return self._form_mode
        if self.request.method.upper() == 'GET':
            return 'read'
        elif self.request.method.upper() == 'POST':
            if self.main_object:
                return 'write'
            return 'creates'
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
        for fname in self.__form_fields_ignore:
            _all_fields.pop(fname, None)
        # remove non-stored fields to exclude computed
        _all_fields = {k: v for k, v in _all_fields.iteritems() if v['store']}
        # update fields attributes
        self._form_update_fields_attributes(_all_fields)
        # update fields order
        if self._form_fields_order:
            _sorted_all_fields = OrderedDict()
            for fname in self._form_fields_order:
                _sorted_all_fields[fname] = _all_fields[fname]
            _all_fields = _sorted_all_fields
        return _all_fields

    def _form_update_fields_attributes(self, _fields):
        """Manipulate fields attributes."""
        for fname in self._form_required_fields:
            # be defensive here since we can remove fields via blacklist
            if fname in _fields:
                _fields[fname]['required'] = True

    @property
    def form_file_fields(self):
        """File fields."""
        return {
            k: v for k, v in self.form_fields().iteritems()
            if v['type'] == 'binary'
        }

    def _form_get_request_values(self):
        # normal fields
        values = {
            k: v for k, v in self.request.form.iteritems()
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
        request_values = request_values or self._form_get_request_values()
        defaults = request_values.copy()
        form_fields = self.form_fields()
        for fname, field in form_fields.iteritems():
            value = None
            # we could have form-only fields (like `custom` in test form below)
            if main_object and fname in main_object:
                value = main_object[fname]
            # maybe a POST request with new values: override item value
            value = request_values.get(fname, value)
            # 1nd lookup for a default type handler
            value_handler = self._form_loaders.get(field['type'], None)
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
            # add `has_*` flags for file fields
            # so in templates we really know if a file field is valued.
            for fname in self.form_file_fields.iterkeys():
                defaults['has_' + fname] = bool(main_object[fname])
        return defaults

    def form_extract_values(self, **request_values):
        """Extract values from request form."""
        request_values = request_values or self._form_get_request_values()
        values = {}
        for fname, field in self.form_fields().iteritems():
            value = request_values.get(fname)
            # 1nd lookup for a default type handler
            value_handler = self._form_extractors.get(field['type'], None)
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


DEFAULT_WIDGETS = {
    # fname or field_type : {
    #      # key of a qweb template
    #     'key': 'cms_form.widget_fname',
    #      # css_klass
    #      'css_klass': 'extra css klasses',
    #      # extra params for particular widgets, JSON compatible
    #     'params': {
    #         'a': 1,
    #     },
    # }
    'many2one': {
        'key': 'cms_form.field_widget_m2o',
    },
    'one2many': {
        'key': 'cms_form.field_widget_x2m',
    },
    'many2many': {
        'key': 'cms_form.field_widget_x2m',
    },
    'date': {
        'key': 'cms_form.field_widget_date',
    },
    'text': {
        'key': 'cms_form.field_widget_text',
    },
    # TODO: we expect an image field to be named "image"
    # but we should handle normal file fields and image fields properly.
    # We should have an 'image' field type...
    'image': {
        'key': 'cms_form.field_widget_image',
    },
}


class CMSForm(models.AbstractModel):
    _name = 'cms.form'
    _inherit = 'cms.form.mixin'

    # template to render the form
    form_template = 'cms_form.base_form'
    form_action = ''
    form_method = 'POST'
    _form_mode = ''
    # extra css klasses for the whole form wrapper
    _form_wrapper_extra_css_klass = ''
    # extra css klasses for just the form element
    _form_extra_css_klass = ''
    _form_validators = {}
    _form_widgets = DEFAULT_WIDGETS
    # internal flag for turning on redirection
    __form_redirect = False
    __form_render_values = {}

    @property
    def form_title(self):
        if self.main_object:
            rec_field = self.main_object[self.form_model._rec_name]
            if hasattr(rec_field, 'id'):
                rec_field = rec_field.name
            title = _('Edit "%s"') % rec_field
        else:
            title = _('Create')
            if self.form_model._description:
                title += ' ' + self.form_model._description
        return title

    @property
    def form_redirect(self):
        return self.__form_redirect

    @form_redirect.setter
    def form_redirect(self, value):
        self.__form_redirect = value

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

    @property
    def form_msg_success_created(self):
        # TODO: include form model name if any
        msg = _('Item created.')
        return msg

    @property
    def form_msg_success_updated(self):
        return _('Item updated.')

    @property
    def form_msg_error_missing(self):
        return _('Some required fields are empty.')

    def form_render(self, override_values=None):
        override_values = override_values or {}
        values = self.form_render_values.copy()
        values.update(override_values)
        return self.env.ref(self.form_template).render(values)

    def form_process(self):
        render_values = self.form_render_values
        handler = getattr(self, 'form_process_' + self.request.method.upper())
        render_values.update(handler(render_values))
        self.form_render_values = render_values

    def form_process_GET(self, render_values):
        form_data = self.form_load_defaults()
        render_values['form_data'] = form_data
        return render_values

    def form_next_url(self, main_object=None):
        main_object = main_object or self.main_object
        if main_object:
            if 'website_url' in main_object:
                return main_object.website_url
        return '/'

    def form_create_or_update(self):
        write_values = self.form_extract_values()
        if self.main_object:
            self.main_object.write(write_values)
            msg = self.form_msg_success_updated
        else:
            self.main_object = self.form_model.create(write_values)
            msg = self.form_msg_success_created
        if msg and self.o_request.website:
            self.o_request.website.add_status_message(msg)
        return self.main_object

    def form_process_POST(self, render_values):
        errors, errors_message = self.form_validate()
        if not errors:
            self.form_create_or_update()
            self.form_success = True
            self.form_redirect = True
        else:
            render_values.update({
                'errors': errors,
                'errors_message': errors_message,
                'form_data': self.form_load_defaults(),
            })
        return render_values

    def _form_check_empty_field(self, field, value):
        if isinstance(value, werkzeug.datastructures.FileStorage):
            # file field w/ no content
            return not bool(value.content_length)
        return value in (False, '')

    def form_validate(self, request_values=None):
        errors = {}
        errors_message = {}
        request_values = request_values or self._form_get_request_values()

        missing = False
        for fname, field in self.form_fields().iteritems():
            value = request_values.get(fname)
            error = False
            if field['required'] \
                    and self._form_check_empty_field(field, value):
                errors[fname] = 'missing'
                missing = True
            # 1nd lookup for a default type validator
            validator = self._form_validators.get(field['type'], None)
            # 2nd lookup for a specific type validator
            validator = getattr(
                self, '_form_validate_' + field['type'], validator)
            # 3rd lookup and override by named validator if any
            validator = getattr(
                self, '_form_validate_' + fname, validator)
            if validator:
                error, error_msg = validator(value, **request_values)
            if error:
                errors[fname] = error
                errors_message[fname] = error_msg

        # error message for empty required fields
        if missing and self.o_request.website:
            msg = self.form_msg_error_missing
            self.o_request.website.add_status_message(msg, mtype='danger')
        return errors, errors_message

    def _form_update_fields_attributes(self, _fields):
        """Override to add widgets."""
        super(CMSForm, self)._form_update_fields_attributes(_fields)
        for fname, field in _fields.iteritems():
            field['widget'] = {}
            for key in (field['type'], fname):
                if key in self._form_widgets:
                    field['widget'] = self._form_widgets[key]
