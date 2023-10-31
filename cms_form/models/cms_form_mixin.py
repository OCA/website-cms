# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import json
from collections import OrderedDict

from odoo import _, api, exceptions, fields, models, tools

from .. import marshallers, utils
from .fields import Serialized

IGNORED_FORM_FIELDS = [
    "display_name",
    "__last_update",
    # TODO: retrieve from inherited schema
    "message_ids",
    "message_follower_ids",
    "message_follower",
    "message_last_post",
    "message_unread",
    "message_unread_counter",
    "message_needaction_counter",
    # Loose dep
    "website_message_ids",
    "website_published",
] + models.MAGIC_COLUMNS


class CMSFormMixin(models.AbstractModel):
    """Base abstract CMS form."""

    _name = "cms.form.mixin"
    _description = "CMS Form mixin"

    id = fields.Id(automatic=True)

    # Special fields /
    # TODO: would be better to have python obj fields
    request = fields.Binary(form_tech=True, store=False)
    o_request = fields.Binary(form_tech=True, store=False)
    main_object = fields.Binary(form_tech=True, store=False, default=None)
    # Values used to render the form
    form_render_values = fields.Binary(
        form_tech=True, store=False, compute="_compute_form_render_values"
    )
    form_data = Serialized(form_tech=True, default={})
    # / special fields
    form_wrapper_template = fields.Char(form_tech=True, default="")
    form_template = fields.Char(form_tech=True, default="cms_form.base_form")
    form_fields_template = fields.Char(
        form_tech=True, default="cms_form.base_form_fields"
    )
    form_fields_wrapper_template = fields.Char(
        form_tech=True, compute="_compute_form_fields_wrapper_template", readonly=False
    )
    form_buttons_template = fields.Char(
        form_tech=True, default="cms_form.base_form_buttons"
    )
    form_display_mode = fields.Selection(
        form_tech=True,
        selection=[("horizontal", "Horizontal"), ("vertical", "Vertical")],
        default="horizontal",
    )
    form_action = fields.Char(form_tech=True, default="")
    form_method = fields.Char(form_tech=True, default="POST")
    form_mode = fields.Char(
        form_tech=True, default="", compute="_compute_form_mode", readonly=False
    )
    form_title = fields.Char(form_tech=True, default="")
    form_description = fields.Char(form_tech=True, default="")
    # extra css klasses for the whole form wrapper
    form_wrapper_extra_css_klass = fields.Char(form_tech=True, default="")
    # extra css klasses for just the form element
    form_extra_css_klass = fields.Char(form_tech=True, default="")
    # model tied to this form
    form_model_name = fields.Char(form_tech=True, default="")
    # model's fields to load
    form_model_fields = Serialized(form_tech=True, default=[])
    # force fields order
    form_fields_order = Serialized(form_tech=True, default=[])
    # quickly force required fields
    form_required_fields = Serialized(form_tech=True, default=[])
    # mark some fields as "sub".
    # For usability reasons you might want to move some fields
    # inside the widget of another field.
    # If you mark a field as "sub" this field
    # won't be included into fields' list as usual
    # but you can still find it in `form_fields` value.
    # 'mainfield': {
    #     # loaded for a specific value
    #     'mainfield_value': ('subfield1', 'subfield2'),
    #     # loaded for all values
    #     '_all': ('subfield3', ),
    # }
    form_sub_fields = Serialized(form_tech=True, default={})
    # fields' attributes to load
    form_fields_attributes = Serialized(
        form_tech=True,
        default=[
            "type",
            "string",
            "domain",
            "required",
            "readonly",
            "relation",
            "store",
            "help",
            "selection",
        ],
    )
    # include only these fields
    form_fields_whitelist = Serialized(form_tech=True, default=[])
    # exclude these fields
    form_fields_blacklist = Serialized(form_tech=True, default=[])
    # include fields but make them input[type]=hidden
    form_fields_hidden = Serialized(form_tech=True, default=[])
    # group form fields together
    # [
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
    # ]
    form_fieldsets = Serialized(form_tech=True, default=[])
    # control fieldset display
    # options:
    # * `tabs` -> rendered as tabs
    # * `vertical` -> one after each other, vertically
    form_fieldsets_display = fields.Selection(
        form_tech=True,
        selection=[("tabs", "Tabs"), ("vertical", "Vertical")],
        default="vertical",
    )
    # extract values mode
    # This param can be used to alter value format
    # when extracting values from request.
    # eg: in write mode you can get on a m2m [(6, 0, [1,2,3])]
    # while in read mode you can get just the ids [1,2,3]
    form_extract_value_mode = fields.Selection(
        form_tech=True,
        selection=[("write", "Write"), ("read", "Read")],
        default="write",
    )
    # ignore this fields default
    form_fields_ignore = Serialized(form_tech=True, default=IGNORED_FORM_FIELDS)
    # default is to post the form and have a full reload. Set to true to keep
    # the search form as it is and only replace the result pane
    form_ajax = fields.Boolean(form_tech=True, default=False)
    form_ajax_onchange = fields.Boolean(form_tech=True, default=False)
    # jQuery selector to find container of search results
    form_content_selector = fields.Char(form_tech=True, default=".form_content")
    # used to interpolate widgets' html field name
    form_fname_pattern = fields.Char(form_tech=True, default="")

    def _valid_field_parameter(self, field, name):
        res = super()._valid_field_parameter(field, name)
        # allow form tech fields
        return name.startswith("form_") or res

    def _compute_form_render_values(self):
        for rec in self:
            rec.form_render_values = rec._get_render_values()

    def _get_render_values(self):
        return {
            # TODO: default for BInary field is "False" but we need "None"
            "main_object": self.main_object or None,
            "form": self,
            "errors": {},
            "errors_messages": {},
        }

    def _compute_form_mode(self):
        for rec in self:
            rec.form_mode = rec._get_form_mode()

    def _get_form_mode(self):
        if self.form_mode:
            # forced mode
            return self.form_mode
        if self.main_object:
            return "edit"
        return "create"

    _form_field_wrapper_template_pattern = (
        "cms_form.form_{form.form_display_mode}_field_wrapper"
    )

    def _compute_form_fields_wrapper_template(self):
        pattern = self._form_field_wrapper_template_pattern
        for rec in self:
            rec.form_fields_wrapper_template = pattern.format(form=rec)

    def form_init(self, request, main_object=None, **kw):
        """Initalize a form instance.

        @param request: an odoo-wrapped werkeug request
        @param main_object: current model instance if any
        @param kw: pass any override for `_form_` attributes
            ie: `fields_attributes` -> `form_fields_attributes`
        """
        vals = {
            "o_request": request,
            "request": request.httprequest,
            "main_object": main_object,
        }
        form_kw = {k: v for k, v in kw.items() if k in self._fields}
        vals.update(form_kw)
        form = self.new(vals)
        if "form_data" not in vals:
            form.form_data = form.form_load_defaults()
        return form

    def form_check_permission(self, raise_exception=True):
        """Check permission on current model and main object if any."""
        res = True
        msg = ""
        if self.main_object:
            if hasattr(self.main_object, "cms_can_edit"):
                res = self.main_object.cms_can_edit()
            else:
                # `cms.info.mixin` not provided by model.
                res = self._can_edit(raise_exception=False)
            msg = _(
                "You cannot edit this record. Model: %(model)s, ID: %(obj_id)s.",
                model=self.main_object._name,
                obj_id=self.main_object.id,
            )
        else:
            if self.form_model_name:
                if hasattr(self.form_model, "cms_can_create"):
                    res = self.form_model.cms_can_create()
                else:
                    res = self._can_create(raise_exception=False)
                msg = (
                    _("You are not allowed to create any record for the model `%s`.")
                    % self.form_model_name
                )
        if raise_exception and not res:
            raise exceptions.AccessError(msg)
        return res

    def _can_create(self, raise_exception=True):
        """Check that current user can create instances of given model."""
        if self.form_model_name:
            return self.form_model.check_access_rights(
                "create", raise_exception=raise_exception
            )
        # just a safe fallback if you call this method directly
        return True

    def _can_edit(self, raise_exception=True):
        """Check that current user can edit main object if any."""
        if not self.main_object:
            # just a safe fallback if you call this method directly
            return True
        try:
            self.main_object.check_access_rights("write")
            self.main_object.check_access_rule("write")
            can = True
        except exceptions.AccessError:
            if raise_exception:
                raise
            can = False
        return can

    @property
    def form_model(self):
        # queue_job tries to read properties. Be defensive.
        return self.env.get(self.form_model_name)

    def form_fields_get(self, hidden=None):
        """Retrieve form fields.

        :param hidden: whether to include or not hidden inputs.
            Options:
            * None, default: include all fields, hidden or not
            * True: include only hidden fields
            * False: include all fields but those hidden.
        """
        _fields = self._form_fields_get()
        # update fields attributes
        self.form_update_fields_attributes(_fields)
        if hidden is not None:
            # make sure ordering is preserved
            filtered = OrderedDict()
            for k, v in _fields.items():
                if v.get("hidden", False) == hidden:
                    filtered[k] = v
            return filtered
        return _fields

    def _form_fields_attributes_get(self):
        return self.form_fields_attributes or []

    @tools.cache("self")
    def _form_fields_get(self):
        """Retrieve form fields ready to be used.

        Fields lookup:
        * model's fields
        * form's fields

        Blacklisted fields are skipped.
        Whitelisted fields are loaded only.
        """
        attributes = self._form_fields_attributes_get()
        _all_fields = OrderedDict()
        # load model fields
        _model_fields = {}
        if self.form_model_name:
            _model_fields = self.form_model.fields_get(
                self.form_model_fields,
                attributes=attributes,
            )
            # inject defaults
            defaults = self.form_model.default_get(self.form_model_fields)
            for k, v in defaults.items():
                _model_fields[k]["_default"] = v
        # load form fields
        _form_fields = self.fields_get(attributes=attributes)
        # inject defaults
        for k, v in self.default_get(list(_form_fields.keys())).items():
            _form_fields[k]["_default"] = v
        _all_fields.update(_model_fields)
        # form fields override model fields
        # TODO: add tests
        _all_fields = utils.data_merge(_all_fields, _form_fields)
        # exclude blacklisted
        for fname in self.form_fields_blacklist:
            # make it fail if passing wrong field name
            _all_fields.pop(fname)
        # include whitelisted
        _all_whitelisted = {}
        for fname in self.form_fields_whitelist:
            _all_whitelisted[fname] = _all_fields[fname]
        _all_fields = _all_whitelisted or _all_fields
        # remove unwanted fields
        self._form_remove_uwanted(_all_fields)
        # remove non-stored fields to exclude computed
        # NOTE: make sure to use `v.get` because sometimes (like for res.users)
        # you can get auto-generated fields here (like `in_group_XX`)
        # whereas some core fields attributes are missing.
        _all_fields = {k: v for k, v in _all_fields.items() if v.get("store")}
        # update fields order
        if self.form_fields_order:
            _sorted_all_fields = OrderedDict()
            for fname in self.form_fields_order:
                # this check is required since you can have `groups` attribute
                # on a field, making the field unavailable if not satisfied.
                if fname in _all_fields:
                    _sorted_all_fields[fname] = _all_fields[fname]
            _all_fields = _sorted_all_fields
        # compute subfields and remove them from all fields if any
        self._form_prepare_subfields(_all_fields)
        return _all_fields

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super().fields_get(allfields, attributes)
        # Wipe tech fields
        return {
            k: v
            for k, v in res.items()
            if not getattr(self._fields[k], "form_tech", False)
        }

    def _form_prepare_subfields(self, _all_fields):
        """Add subfields to related main fields."""
        # TODO: document this
        for mainfield, subfields in self.form_sub_fields.items():
            if mainfield not in _all_fields:
                continue
            _subfields = {}
            for val, subs in subfields.items():
                _subfields[val] = {}
                for sub in subs:
                    if sub in _all_fields:
                        _subfields[val][sub] = _all_fields[sub]
                        _all_fields[sub]["is_subfield"] = True
            _all_fields[mainfield]["subfields"] = _subfields

    def _form_remove_uwanted(self, _all_fields):
        """Remove fields from form fields."""
        for fname in self.form_fields_ignore:
            _all_fields.pop(fname, None)

    def form_fieldsets_get(self):
        # exclude empty ones
        form_fields = self._form_fields_get()
        res = []
        for fset in self.form_fieldsets:
            if any([form_fields.get(fname) for fname in fset["fields"]]):
                # at least one field is here
                res.append(fset)
        return res

    @property
    def form_fieldsets_wrapper_klass(self):
        klass = []
        if self.form_fieldsets:
            klass = ["has_fieldsets", self.form_fieldsets_display]
        return " ".join(klass)

    def form_update_fields_attributes(self, _fields):
        """Manipulate fields attributes."""
        for fname, field in _fields.items():
            if fname in self.form_required_fields:
                _fields[fname]["required"] = True
            if self._form_is_field_hidden(fname, field):
                _fields[fname]["hidden"] = True
            _fields[fname]["widget"] = self.form_get_widget(fname, field)

    def _form_is_field_hidden(self, fname, field):
        return (
            fname in self.form_fields_hidden
            or fname in self._fields
            and getattr(self._fields[fname], "form_hidden", False)
        )

    def form_get_field_wrapper_template(self, fname, field):
        return field["widget"].w_wrapper_template or self.form_fields_wrapper_template

    def _form_get_default_widget_model(self, fname, field):
        """Retrieve widget model name."""
        if field.get("hidden"):
            # special case
            return "cms.form.widget.hidden"
        widget_model = "cms.form.widget.char"
        for key in (field["type"], fname):
            model_key = "cms.form.widget." + key
            if model_key in self.env:
                widget_model = model_key
        return widget_model

    def form_get_widget(self, fname, field, **kw):
        """Retrieve and initialize widget."""
        specific_widget = self._form_get_specific_widget(fname, field, **kw)
        if specific_widget:
            return specific_widget
        model = self._form_get_default_widget_model(fname, field)
        return self.env[model].widget_init(self, fname, field, **kw)

    def form_get_current_widget(self, fname):
        return self.form_fields_get()[fname]["widget"]

    def _form_get_specific_widget(self, fname, field, **kw):
        """Retrieve and initialize fields' specific widgets.

        Form fields' can declare custom widgets using `form_widget` attribute.
        Properties:

        `resolver`: callable that returns a widget already initialized (optional)
        `model`: widget model if no `resolver` is passed (mandatory)
        `options`: dictionary or callable to resolve widget's options
        """
        widget_conf = {}
        if fname in self._fields:
            # Note: a custom widget for a field on the related model
            # can come only from an override of the field in the form.
            widget_conf = getattr(self._fields[fname], "form_widget", {})
        if not widget_conf:
            return None
        if widget_conf.get("resolver"):
            return widget_conf["resolver"](self, fname, field, **kw)
        try:
            model = widget_conf["model"]
        except KeyError:
            model = self._form_get_default_widget_model(fname, field)
        options = widget_conf.get("options", {})
        if options and callable(options):
            options = options(self, fname, field, **kw)
        return self.env[model].widget_init(self, fname, field, **options)

    @property
    def form_file_fields(self):
        """File fields."""
        return {
            k: v for k, v in self.form_fields_get().items() if v["type"] == "binary"
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
        files = self.request.files
        # Convert files always. Main reasons:
        # * file descriptors will be consumed on 1st read.
        #   If you access them again you won't find any info.
        # * homegenous handling of files
        # * no need to parse metadata down the stack as is done by the marshaller
        parsed_files = getattr(self.request, "_cms_form_files_processed", None)
        if files and not parsed_files:
            _file_values = {}
            _file_fields = self.form_file_fields
            for fname, fobj in files.items():
                if fname in _file_fields:
                    # fake field name enforcing marshaller
                    if not fname.endswith(":file"):
                        fname = f"{fname}:file"
                    _file_values[fname] = fobj
            file_values = marshallers.marshal_request_values(_file_values)
            self.request._cms_form_files_processed = file_values
        elif parsed_files:
            res.update(parsed_files)
        return res

    # TODO: rename to form_load
    # TODO: adapt signature to form_extract (eg: kw args)
    def form_load_defaults(self, main_object=None, request_values=None):
        """Load default values.

        Values lookup order:

        1. `main_object` fields' values (if an existing main_object is passed)
        2. request parameters (only parameters matching form fields names)
        """
        if self.form_data:
            return self.form_data
        main_object = main_object or self.main_object
        request_values = request_values or self.form_get_request_values()
        defaults = request_values.copy()
        form_fields = self.form_fields_get()
        for fname, field in form_fields.items():
            value = field["widget"].w_load(**request_values)
            # override via specific form loader when needed
            loader = self.form_get_loader(
                fname, field, main_object=main_object, value=value, **request_values
            )
            if loader:
                value = loader(fname, field, value, **request_values)
            defaults[fname] = value
        return defaults

    def form_get_loader(self, fname, field, main_object=None, value=None, **req_values):
        """Retrieve form value loader.

        :param fname: field name
        :param field: field description as `fields_get`
        :param main_object: current main object if any
        :param value: current field value if any
        :param req_values: custom request valuess
        """
        # lookup for a specific type loader method
        loader = getattr(self, "_form_load_" + field["type"], None)
        # 3rd lookup and override by named loader if any
        loader = getattr(self, "_form_load_" + fname, loader)
        return loader

    # TODO: rename to form_extract
    def form_extract_values(self, **request_values):
        """Extract values from request form."""
        request_values = request_values or self.form_get_request_values()
        values = {}
        for fname, field in self.form_fields_get().items():
            value = field["widget"].w_extract(**request_values)
            # override via specific form extractor when needed
            extractor = self.form_get_extractor(
                fname, field, value=value, **request_values
            )
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
        extractor = getattr(self, "_form_extract_" + field["type"], None)
        # 3rd lookup and override by named handler if any
        extractor = getattr(self, "_form_extract_" + fname, extractor)
        return extractor

    def form_render(self, **kw):
        """Renders form template declared in `form_template`.

        To render the form simply do:

            <t t-out="form.form_render()" />
        """
        values = self.form_render_values.copy()
        values.update(kw)
        return self.env["ir.qweb"]._render(self.form_template, values)

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
        handler = getattr(self, "form_process_" + self.request.method.upper())
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
        * `form_wrapper_extra_css_klass` extra klasses from form attribute
        * `mode_` + form mode (ie: 'mode_write')
        """
        parts = [
            "cms_form_wrapper",
            self._name.replace(".", "_").lower(),
            self.form_model_name.replace(".", "_").lower(),
            self.form_wrapper_extra_css_klass,
            "mode_" + self.form_mode,
        ]
        return " ".join([x.strip() for x in parts if x.strip()])

    @property
    def form_css_klass(self):
        """Return `<form />` element css klasses.

        By default you can provide extra klasses via `form_extra_css_klass`.
        """
        klass = ""
        if self.form_display_mode == "horizontal":
            klass = "form-horizontal"
        elif self.form_display_mode == "vertical":
            # actually not a real BS3 css klass but helps styling
            klass = "form-vertical"
        if self.form_extra_css_klass:
            klass += " " + self.form_extra_css_klass
        return klass

    def form_make_field_wrapper_klass(self, fname, field, **kw):
        """Return specific CSS klass for the field wrapper."""
        klass = [
            "form-group",
            "form-field",
            "field-{type}",
            "field-{fname}",
        ]
        if field["required"]:
            klass.append("field-required")
        if kw.get("errors", {}).get(fname):
            klass.append("has-error")
        if field["widget"].w_wrapper_css_klass:
            klass.append(field["widget"].w_wrapper_css_klass)
        return " ".join(klass).format(fname=fname, **field)

    def _form_json_info(self):
        info = {}
        info.update(
            {
                "master_slave": self._form_master_slave_info(),
                "model": self.form_model_name,
                "form_content_selector": self.form_content_selector,
            }
        )
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
