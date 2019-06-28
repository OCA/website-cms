# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import inspect
import json
from collections import OrderedDict

from odoo import models, tools, exceptions, _

from .. import utils
from .. import marshallers


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
    form_display_mode = 'horizontal'  # or 'vertical'
    form_action = ''
    form_method = 'POST'
    _form_mode = ''
    # extra css klasses for the whole form wrapper
    _form_wrapper_extra_css_klass = ''
    # extra css klasses for just the form element
    _form_extra_css_klass = ''
    # model tied to this form
    _form_model = ''
    # model's fields to load
    _form_model_fields = []
    # force fields order
    _form_fields_order = []
    # quickly force required fields
    _form_required_fields = ()
    # mark some fields as "sub".
    # For usability reasons you might want to move some fields
    # inside the widget of another field.
    # If you mark a field as "sub" this field
    # won't be included into fields' list as usual
    # but you can still find it in `form_fields` value.
    _form_sub_fields = {
        # 'mainfield': {
        #     # loaded for a specific value
        #     'mainfield_value': ('subfield1', 'subfield2'),
        #     # loaded for all values
        #     '_all': ('subfield3', ),
        # }
    }
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
    # include fields but make them input[type]=hidden
    _form_fields_hidden = ()
    # group form fields together
    _form_fieldsets = [
        # {
        #     'id': 'main',
        #     'title': 'My group of fields',
        #     'description': 'Bla bla bla',
        #     'fields': ['name', 'age', 'foo'],
        #     'css_extra_klass': 'best_fieldset',
        # },
        # {
        #     'id': 'extras',
        #     'title': 'My group of fields 2',
        #     'description': 'Bla bla bla',
        #     'fields': ['some', 'other', 'field'],
        #     'css_extra_klass': '',
        # },
    ]
    # control fieldset display
    # options:
    # * `tabs` -> rendered as tabs
    # * `vertical` -> one after each other, vertically
    _form_fieldsets_display = 'vertical'
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
    # default is to post the form and have a full reload. Set to true to keep
    # the search form as it is and only replace the result pane
    _form_ajax = False
    # submit the form for every change event
    _form_ajax_onchange = False

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
        for k, v in kw.items():
            attr = getattr(form, '_form_' + k, '__no__attr__')
            if attr != '__no__attr__' and not inspect.ismethod(attr):
                setattr(form, '_form_' + k, v)
        return form

    def form_check_permission(self, raise_exception=True):
        """Check permission on current model and main object if any."""
        res = True
        msg = ''
        if self.main_object:
            if hasattr(self.main_object, 'cms_can_edit'):
                res = self.main_object.cms_can_edit()
            else:
                # not `website.published.mixin` model
                # TODO: probably is better to move such methods
                # defined in `cms_info` to `base` model instead.
                # You might want to use a form on an a non-website model.
                # This should be considered if we move away from `website`
                # as a base and rely only on `portal` features.
                res = self._can_edit(raise_exception=False)
            msg = _(
                'You cannot edit this record. Model: %s, ID: %s.'
            ) % (self.main_object._name, self.main_object.id)
        else:
            if self._form_model:
                if hasattr(self.form_model, 'cms_can_create'):
                    res = self.form_model.cms_can_create()
                else:
                    # not `website.published.mixin` model
                    res = self._can_create(raise_exception=False)
                msg = _(
                    'You are not allowed to create any record '
                    'for the model `%s`.'
                ) % self._form_model
        if raise_exception and not res:
            raise exceptions.AccessError(msg)
        return res

    def _can_create(self, raise_exception=True):
        """Check that current user can create instances of given model."""
        if self._form_model:
            return self.form_model.check_access_rights(
                'create', raise_exception=raise_exception)
        # just a safe fallback if you call this method directly
        return True

    def _can_edit(self, raise_exception=True):
        """Check that current user can edit main object if any."""
        if not self.main_object:
            # just a safe fallback if you call this method directly
            return True
        try:
            self.main_object.check_access_rights('write')
            self.main_object.check_access_rule('write')
            can = True
        except exceptions.AccessError:
            if raise_exception:
                raise
            can = False
        return can

    @property
    def form_title(self):
        return ''  # pragma: no cover

    @property
    def form_description(self):
        return ''  # pragma: no cover

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
        # queue_job tries to read properties. Be defensive.
        return self.env.get(self._form_model)

    def form_fields(self, hidden=None):
        """Retrieve form fields.

        :param hidden: whether to include or not hidden inputs.
            Options:
            * None, default: include all fields, hidden or not
            * True: include only hidden fields
            * False: include all fields but those hidden.
        """
        _fields = self._form_fields()
        # update fields attributes
        self.form_update_fields_attributes(_fields)
        if hidden is not None:
            # make sure ordering is preserved
            filtered = OrderedDict()
            for k, v in _fields.items():
                if v.get('hidden', False) == hidden:
                    filtered[k] = v
            return filtered
        return _fields

    @tools.cache('self')
    def _form_fields(self):
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
            # inject defaults
            defaults = self.form_model.default_get(self._form_model_fields)
            for k, v in defaults.items():
                _model_fields[k]['_default'] = v
        # load form fields
        _form_fields = self.fields_get(attributes=self._form_fields_attributes)
        # inject defaults
        for k, v in self.default_get(list(_form_fields.keys())).items():
            _form_fields[k]['_default'] = v
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
        # NOTE: make sure to use `v.get` because sometimes (like for res.users)
        # you can get auto-generated fields here (like `in_group_XX`)
        # whereas some core fields attributes are missing.
        _all_fields = {k: v for k, v in _all_fields.items() if v.get('store')}
        # update fields order
        if self._form_fields_order:
            _sorted_all_fields = OrderedDict()
            for fname in self._form_fields_order:
                # this check is required since you can have `groups` attribute
                # on a field, making the field unavailable if not satisfied.
                if fname in _all_fields:
                    _sorted_all_fields[fname] = _all_fields[fname]
            _all_fields = _sorted_all_fields
        # compute subfields and remove them from all fields if any
        self._form_prepare_subfields(_all_fields)
        return _all_fields

    def _form_prepare_subfields(self, _all_fields):
        """Add subfields to related main fields."""
        # TODO: test this
        for mainfield, subfields in self._form_sub_fields.items():
            if mainfield not in _all_fields:
                continue
            _subfields = {}
            for val, subs in subfields.items():
                _subfields[val] = {}
                for sub in subs:
                    if sub in _all_fields:
                        _subfields[val][sub] = _all_fields[sub]
                        _all_fields[sub]['is_subfield'] = True
            _all_fields[mainfield]['subfields'] = _subfields

    def _form_remove_uwanted(self, _all_fields):
        """Remove fields from form fields."""
        for fname in self.__form_fields_ignore:
            _all_fields.pop(fname, None)

    def form_fieldsets(self):
        # exclude empty ones
        form_fields = self._form_fields()
        res = []
        for fset in self._form_fieldsets:
            if any([form_fields.get(fname) for fname in fset['fields']]):
                # at least one field is here
                res.append(fset)
        return res

    @property
    def form_fieldsets_wrapper_klass(self):
        klass = []
        if self._form_fieldsets:
            klass = ['has_fieldsets', self._form_fieldsets_display]
        return ' '.join(klass)

    def form_update_fields_attributes(self, _fields):
        """Manipulate fields attributes."""
        for fname, field in _fields.items():
            if fname in self._form_required_fields:
                _fields[fname]['required'] = True
            if fname in self._form_fields_hidden:
                _fields[fname]['hidden'] = True
            _fields[fname]['widget'] = self.form_get_widget(fname, field)

    @property
    def form_widgets(self):
        """Return a mapping between field name and widget model."""
        return {}

    def form_get_widget_model(self, fname, field):
        """Retrieve widget model name."""
        if field.get('hidden'):
            # special case
            return 'cms.form.widget.hidden'
        widget_model = 'cms.form.widget.char'
        for key in (field['type'], fname):
            model_key = 'cms.form.widget.' + key
            if model_key in self.env:
                widget_model = model_key
        return self.form_widgets.get(fname, widget_model)

    def form_get_widget(self, fname, field, **kw):
        """Retrieve and initialize widget."""
        return self.env[self.form_get_widget_model(fname, field)].widget_init(
            self, fname, field, **kw
        )

    @property
    def form_file_fields(self):
        """File fields."""
        return {
            k: v for k, v in self.form_fields().items()
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
        res = marshallers.marshal_request_values(_values)
        # file fields
        res.update(
            {k: v for k, v in self.request.files.items()}
        )
        return res

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
        for fname, field in form_fields.items():
            value = field['widget'].w_load(**request_values)
            # override via specific form loader when needed
            loader = self.form_get_loader(
                fname, field,
                main_object=main_object, value=value, **request_values)
            if loader:
                value = loader(fname, field, value, **request_values)
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
        # lookup for a specific type loader method
        loader = getattr(
            self, '_form_load_' + field['type'], None)
        # 3rd lookup and override by named loader if any
        loader = getattr(
            self, '_form_load_' + fname, loader)
        return loader

    def form_extract_values(self, **request_values):
        """Extract values from request form."""
        request_values = request_values or self.form_get_request_values()
        values = {}
        for fname, field in self.form_fields().items():
            value = field['widget'].w_extract(**request_values)
            # override via specific form extractor when needed
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
        # lookup for a specific type handler
        extractor = getattr(
            self, '_form_extract_' + field['type'], None)
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
        values['field_wrapper_template'] = \
            'cms_form.form_{}_field_wrapper'.format(self.form_display_mode)
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
        self.form_render_values = dict(render_values, **handler(render_values))

    def form_process_GET(self, render_values):
        """Process GET requests."""
        return render_values  # pragma: no cover

    def form_process_POST(self, render_values):
        """Process POST requests."""
        raise NotImplementedError()  # pragma: no cover

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
            self._name.replace('.', '_').lower(),
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
        klass = ''
        if self.form_display_mode == 'horizontal':
            klass = 'form-horizontal'
        elif self.form_display_mode == 'vertical':
            # actually not a real BS3 css klass but helps styling
            klass = 'form-vertical'
        if self._form_extra_css_klass:
            klass += ' ' + self._form_extra_css_klass
        return klass

    def form_make_field_wrapper_klass(self, fname, field, **kw):
        """Return specific CSS klass for the field wrapper."""
        klass = [
            'form-group',
            'form-field',
            'field-{type}',
            'field-{fname}',
        ]
        if field['required']:
            klass.append('field-required')
        if kw.get('errors', {}).get(fname):
            klass.append('has-error')
        return ' '.join(klass).format(fname=fname, **field)

    def _form_json_info(self):
        info = {}
        info.update({
            'master_slave': self._form_master_slave_info(),
            'model': self._form_model,
            'form_content_selector': getattr(
                self, '_form_content_selector', None,
            ),
        })
        return info

    def form_json_info(self):
        return json.dumps(self._form_json_info())

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
        return utils.data_merge(info, tomerge)
