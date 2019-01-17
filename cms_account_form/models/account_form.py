# Copyright 2018 Simone Orsi - Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, exceptions, _
from odoo.addons.base.ir.ir_mail_server import MailDeliveryException

import logging
_logger = logging.getLogger(__name__)
try:
    from validate_email import validate_email
except ImportError:  # pragma: no cover
    _logger.debug("Cannot import `validate_email`.")


class AccountForm(models.AbstractModel):
    """Partner account form."""

    _name = 'cms.form.my.account'
    _inherit = 'cms.form'
    _form_model = 'res.partner'
    _form_model_fields = (
        'name',
        'vat',
        'street',
        'zip',
        'city',
        'country_id',
        'phone',
        'email',
        'website',
        'image',
    )
    _form_fields_order = _form_model_fields
    _form_required_fields = (
        "name", "street", "zip", "city",
        "country_id", "phone", "email"
    )

    @property
    def form_title(self):  # pragma: no cover
        return _('My account')

    @property
    def form_msg_success_updated(self):  # pragma: no cover
        return _('Profile updated.')

    def form_next_url(self, main_object=None):
        if self.request.args.get('redirect'):
            # redirect overridden
            return self.request.args.get('redirect')
        return '/my/home'

    def form_update_fields_attributes(self, _fields):
        """Set warning message for email updates."""
        super().form_update_fields_attributes(_fields)
        tmpl = self.env.ref('cms_account_form.email_field_update_warning')
        _fields['email']['help'] = tmpl.render({})

    def _form_validate_email(self, value, **req_values):
        error, message = None, None
        if value and not validate_email(value):
            error = 'email_not_valid'
            message = _('Invalid Email! Please enter a valid email address.')
        return error, message

    def _form_validate_vat(self, value, **req_values):
        error, message = None, None
        if value and hasattr(self.form_model, 'check_vat'):
            country_id = int(req_values.get("country_id", 0))
            if country_id:
                value = self.form_model.fix_eu_vat_number(country_id, value)
            partner_dummy = self.form_model.new({
                'vat': value,
                'country_id': country_id or False,
            })
            try:
                partner_dummy.check_vat()
            except exceptions.ValidationError as err:
                error = 'vat_not_valid'
                message = err.name
        return error, message

    def form_before_create_or_update(self, values, extra_values):
        user = self.env.user
        # handle email update
        if 'email' in values and user.email != values.get('email'):
            self._handle_email_update(user, values)

    def _handle_email_update(self, user, values):
        """Validate email update and handle login update.

        :param user: res.users record
        :param values: form request values

        If email is validated:

            * check if already exists
            * if yes, provide an error message
            * if not, updates user's login
            * provide an info message
            * logout current session to force re-login with new email
        """
        email = values['email']
        # TODO: this could be useless as we validate w/ `_form_validate_email`
        valid = validate_email(email)
        if email and valid and not user._is_admin():
            exists = user.with_context(active_test=False).sudo().search_count(
                ['|', ('login', '=', email), ('email', '=', email)]
            )
            if exists and self.o_request.website:
                # prevent email save and display friendly message
                del values['email']
                self._handle_email_exists(email)
                return False
            try:
                self._handle_login_update(email, user)
                can_change = True
            except MailDeliveryException:
                # do not update email / login
                # if for any reason we cannot send email
                can_change = False
            if can_change and self.o_request.website:
                self._logout_and_notify(email)
            return True
        return False

    def _handle_email_exists(self, email):
        title = _('Warning')
        msg = _('Email address `%s` already taken.') % email
        self.o_request.website.add_status_message(
            msg, type_='warning', title=title)

    def _handle_login_update(self, email, user):
        # update login on user
        # this MUST happen BEFORE `reset_password` call
        # otherwise it will not find the user to reset!
        user.sudo().write(
            {'login': email, 'email': email, }
        )
        # send reset password link to verify email
        user.sudo().reset_password(email)

    def _logout_and_notify(self, email):
        # force log out
        self.o_request.session.logout(keep_db=True)
        # add message
        title = _('Important')
        msg = _(
            'Your login username has changed to: `%s`. '
            'An email has been sent to verify it. '
            'You will be asked to reset your password.'
        ) % email
        self.o_request.website.add_status_message(
            msg, type_='warning', title=title)
