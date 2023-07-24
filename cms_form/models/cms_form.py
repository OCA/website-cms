# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


import psycopg2 as pg

from odoo import _, exceptions, fields, models

from .fields import Serialized


class CMSForm(models.AbstractModel):
    _name = "cms.form"
    _description = "CMS Form"
    _inherit = "cms.form.mixin"

    # internal flag for successful form
    form_success = fields.Boolean(form_tech=True, default=False)
    # internal flag for turning on redirection
    form_redirect = fields.Boolean(form_tech=True, default=False)
    # default validators by field type
    # 'many2one': 'my_validation_method'
    form_validators = Serialized(form_tech=True, default={})
    # make it computed
    form_title = fields.Char(form_tech=True, compute="_compute_form_title")

    def _compute_form_title(self):
        for rec in self:
            rec.form_title = rec._get_form_title()

    def _get_form_title(self):
        if not self.form_model_name:
            return ""
        if self.main_object:
            rec_field = self.main_object[self.form_model._rec_name]
            if hasattr(rec_field, "id"):
                rec_field = rec_field.name
            title = _('Edit "%s"') % rec_field
        else:
            title = _("Create %s")
            if self.form_model_name:
                model = (
                    self.env["ir.model"]
                    .sudo()
                    .search([("model", "=", self.form_model_name)])
                )
                name = model and model.name or ""
                title = _("Create %s") % name
        return title

    @property
    def form_msg_success_created(self):
        # TODO: include form model name if any
        msg = _("Item created.")
        return msg

    @property
    def form_msg_success_updated(self):
        return _("Item updated.")

    @property
    def form_msg_error_missing(self):
        return _("Some required fields are empty.")

    def form_next_url(self, main_object=None):
        """URL to redirect to after successful form submission."""
        if self.request.args.get("redirect"):
            # redirect overridden
            return self.request.args.get("redirect")
        main_object = main_object or self.main_object
        if main_object and "url" in main_object._fields:
            return main_object.url
        return "/"

    def form_cancel_url(self, main_object=None):
        """URL to redirect to after click on "cancel" button."""
        if self.request.args.get("redirect"):
            # redirect overridden
            return self.request.args.get("redirect")
        main_object = main_object or self.main_object
        if main_object and "url" in main_object._fields:
            return main_object.url
        return self.request.referrer or "/"

    def form_check_empty_value(self, fname, field, value, **req_values):
        """Return True if passed field value is really empty."""
        # delegate to each specific widget
        return field["widget"].w_check_empty_value(value, **req_values)

    def form_validate(self, request_values=None):
        """Validate submitted values."""
        errors = {}
        errors_message = {}
        request_values = request_values or self.form_get_request_values()

        missing = False
        for fname, field in self.form_fields_get().items():
            value = request_values.get(fname)
            error = False
            if field["required"] and self.form_check_empty_value(
                fname, field, value, **request_values
            ):
                errors[fname] = "missing"
                missing = True
            validator = self.form_get_validator(fname, field)
            if validator:
                error, error_msg = validator(value, **request_values)
            if error:
                errors[fname] = error
                errors_message[fname] = error_msg

        # error message for empty required fields
        if missing:
            msg = self.form_msg_error_missing
            self.add_status_message(msg, kind="danger")
        return errors, errors_message

    def form_get_validator(self, fname, field):
        """Retrieve field validator."""
        # 1nd lookup for a default type validator
        validator = self.form_validators.get(field["type"], None)
        # 2nd lookup for a specific type validator
        validator = getattr(self, "_form_validate_" + field["type"], validator)
        # 3rd lookup and override by named validator if any
        validator = getattr(self, "_form_validate_" + fname, validator)
        return validator

    def form_before_create_or_update(self, values, extra_values):
        """Pre create/update hook."""

    def form_after_create_or_update(self, values, extra_values):
        """Post create/update hook."""

    def _form_purge_non_model_fields(self, values):
        """Purge fields that are not in `form_model` schema and return them."""
        extra_values = {}
        if not self.form_model_name:
            return extra_values
        _model_fields = list(
            self.form_model.fields_get(
                self.form_model_fields,
                attributes=self.form_fields_attributes,
            ).keys()
        )
        submitted_keys = list(values.keys())
        for fname in submitted_keys:
            if fname not in _model_fields:
                extra_values[fname] = values.pop(fname)
        return extra_values

    def _form_write(self, values):
        """Just write on the main object."""
        # pass a copy to avoid pollution of initial values by odoo
        self.main_object.write(values.copy())

    def _form_create(self, values):
        """Just create the main object."""
        # pass a copy to avoid pollution of initial values by odoo
        self.main_object = self.form_model.create(values.copy())

    def form_create_or_update(self):
        """Prepare values and create or update main_object."""
        write_values = self.form_extract_values()
        extra_values = self._form_purge_non_model_fields(write_values)
        # pre hook
        self.form_before_create_or_update(write_values, extra_values)
        if self.main_object:
            self._form_write(write_values)
            msg = self.form_msg_success_updated
        else:
            self._form_create(write_values)
            msg = self.form_msg_success_created
        # post hook
        self.form_after_create_or_update(write_values, extra_values)
        if msg:
            self.add_status_message(msg)
        return self.main_object

    def form_process_POST(self, render_values):
        """Process POST requests."""
        errors, errors_message = self.form_validate()
        # Do not flush to keep the caches of current in memory objects
        savepoint = self.env.cr.savepoint(flush=False)
        if not errors:
            try:
                self.form_create_or_update()
                self.form_success = True
                self.form_redirect = True
                return render_values
            except exceptions.ValidationError as err:
                # sounds like there's no way to validate fields
                # before calling write or create,
                # hence we are forced to do it here.
                errors["_validation"] = True
                # err message can be something like
                # u'Error while validating constraint\n
                #    \nEnd Date cannot be set before Start Date.\nNone'
                errors_message["_validation"] = "<br />".join(
                    [
                        x
                        for x in err.args[0].replace("None", "").split("\n")
                        if x.strip()
                    ]
                )
            except (pg.IntegrityError, pg.OperationalError) as err:
                errors["_integrity"] = True
                errors_message["_integrity"] = "<br />".join(
                    [x for x in str(err).split("\n") if x.strip()]
                )
        savepoint.rollback()
        # TODO: how to handle validation error on create?
        # If you use @api.constrains to validate fields' value
        # the check happens only AFTER the record has been created.
        # So, on the 1st submit the record is created
        # and the user is not aware of it since it gets redirected to the form
        # with errors highlighted. He corrects the error and submit again.
        # If no errors, he gets redirected to the new record, ANOTHER record.
        # In the end: we get 2 duplicated objects :(
        # To avoid this beforehand we need validation on JS side +
        # pre-validation (where possible) before create or write.

        self.form_success = False
        # handle ORM validation error
        orm_error = errors.get("_validation") or errors.get("_integrity")
        if orm_error:
            msg = errors_message.get("_validation") or errors_message.get("_integrity")
            if msg:
                self.add_status_message(
                    msg, kind="danger", title=None, dismissible=False
                )
        render_values.update({"errors": errors, "errors_message": errors_message})
        return render_values

    def add_status_message(self, msg, **kw):
        self.env["ir.http"].add_status_message(msg, request=self.o_request, **kw)
