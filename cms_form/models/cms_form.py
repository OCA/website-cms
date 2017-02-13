# -*- coding: utf-8 -*-
# Copyright 2016 Simone Orsi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models
from openerp import exceptions
from openerp import _

import werkzeug
from psycopg2 import IntegrityError


class CMSForm(models.AbstractModel):
    _name = 'cms.form'
    _inherit = 'cms.form.mixin'

    _form_validators = {}

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
        if self.main_object:
            rec_field = self.main_object[self.form_model._rec_name]
            if hasattr(rec_field, 'id'):
                rec_field = rec_field.name
            title = _('Edit "%s"') % rec_field
        else:
            title = _('Create %s')
            if self._form_model:
                model = self.env['ir.model'].search(
                    [('model', '=', self._form_model)])
                name = model and model.name or ''
                title = _('Create %s') % name
        return title

    # internal flag for turning on redirection
    __form_redirect = False

    @property
    def form_redirect(self):
        return self.__form_redirect

    @form_redirect.setter
    def form_redirect(self, value):
        self.__form_redirect = value

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

    def form_next_url(self, main_object=None):
        """URL to redirect to after successful form submission."""
        main_object = main_object or self.main_object
        if main_object and 'website_url' in main_object:
            return main_object.website_url
        return '/'

    def form_cancel_url(self, main_object=None):
        """URL to redirect to after click on "cancel" button."""
        main_object = main_object or self.main_object
        if main_object and 'website_url' in main_object:
            return main_object.website_url
        return self.request.referrer or '/'

    def form_check_empty_field(self, fname, field, value, **req_values):
        """Return True if passed field value is really empty."""
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

    def form_validate(self, request_values=None):
        errors = {}
        errors_message = {}
        request_values = request_values or self.form_get_request_values()

        missing = False
        for fname, field in self.form_fields().iteritems():
            value = request_values.get(fname)
            error = False
            if field['required'] \
                    and self.form_check_empty_field(
                        fname, field, value, **request_values):
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
            self.o_request.website.add_status_message(msg, type_='danger')
        return errors, errors_message

    def form_before_create_or_update(self, values):
        pass

    def form_after_create_or_update(self, values):
        pass

    def form_create_or_update(self):
        # TODO: purge fields that are not in model schema
        write_values = self.form_extract_values()
        # pre hook
        self.form_before_create_or_update(write_values)
        if self.main_object:
            self.main_object.write(write_values)
            msg = self.form_msg_success_updated
        else:
            self.main_object = self.form_model.create(write_values)
            msg = self.form_msg_success_created
        if msg and self.o_request.website:
            self.o_request.website.add_status_message(msg)
        # post hook
        self.form_after_create_or_update(write_values)
        return self.main_object

    def form_process_POST(self, render_values):
        errors, errors_message = self.form_validate()
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
                errors['_validation'] = True
                # err message can be something like
                # u'Error while validating constraint\n
                #    \nEnd Date cannot be set before Start Date.\nNone'
                errors_message['_validation'] = '<br />'.join([
                    x for x in err.name.replace('None', '').split('\n')
                    if x.strip()
                ])
            except IntegrityError as err:
                errors['_integrity'] = True
                errors_message['_integrity'] = '<br />'.join([
                    x for x in err.message.replace('None', '').split('\n')
                    if x.strip()
                ])

        self.form_success = False
        # handle ORM validation error
        orm_error = errors.get('_validation') or errors.get('_integrity')
        if orm_error:
            msg = errors_message.get('_validation') \
                or errors_message.get('_integrity')
            if msg and self.o_request.website:
                self.o_request.website.add_status_message(
                    msg, type_='danger', title=None)
        render_values.update({
            'errors': errors,
            'errors_message': errors_message,
        })
        return render_values
