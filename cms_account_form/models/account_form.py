# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp import models, _
from openerp import SUPERUSER_ID
from openerp.addons.base.ir.ir_mail_server import MailDeliveryException

import logging
_logger = logging.getLogger(__name__)
try:
    from validate_email import validate_email
except ImportError:
    _logger.debug("Cannot import `validate_email`.")


class PartnerForm(models.AbstractModel):
    """Partner model form."""

    _name = 'cms.form.res.partner'
    _inherit = 'cms.form'
    _form_model = 'res.partner'
    _form_fields_order = (
        'image',
        'name',
        'street',
        'zip',
        'city',
        'country_id',
        'phone',
        'email',
        'website',
        'website_short_description',
        'category_id',
    )
    _form_required_fields = (
        "name", "street", "zip", "city",
        "country_id", "phone", "email"
    )

    @property
    def form_title(self):
        return _('My account')

    @property
    def form_msg_success_updated(self):
        return _('Profile updated.')

    def form_validate_email(self, value, **req_values):
        error, message = None, None
        if value and not validate_email(value):
            error = 'email_not_valid'
            message = _('Invalid Email! Please enter a valid email address.')
        return error, message

    def form_before_create_or_update(self, values, extra_values):
        user = self.env.user
        # handle email update
        if 'email' in values and user.email != values.get('email'):
            self._handle_email_update(user, values)

    def form_after_create_or_update(self, values, extra_values):
        partner = self.main_object
        if partner.type == "contact":
            # update address fields
            address_fields = {}
            for key in ('city', 'street', 'street2', 'zip', 'country_id'):
                if key in values:
                    address_fields[key] = values[key]
            if address_fields:
                partner.commercial_partner_id.sudo().write(address_fields)

    def _handle_email_update(self, user, values):
        """Validate email update and handle login update.

        Features:

            * validate email

        if email is validated:

            * check if already exists
            * if yes, provide an error message
            * if not, updates user's login
            * provide an info message
            * logout current session to force re-login with new email
        """
        email = values['email']
        # TODO: this could be useless as we validate w/ `form_validate_email`
        valid = validate_email(email)
        if email and valid and user.id != SUPERUSER_ID:
            exists = user.sudo().search_count(
                ['|', ('login', '=', email), ('email', '=', email)]
            )
            # prevent email save and display friendly message
            values.pop('email')
            if exists and self.o_request.website:
                title = _('Warning')
                msg = _(
                    'Email address `%s` already taken. '
                    'Please check inside your company. '
                ) % email
                self.o_request.website.add_status_message(
                    msg, type_='warning', title=title)
                return False
            try:
                # update login on user
                # this MUST happen BEFORE `reset_password` call
                # otherwise it will not find the user to reset!
                user.sudo().write(
                    {'login': email, 'email': email, }
                )
                # send reset password link to verify email
                user.sudo().reset_password(email)
                can_change = True
            except MailDeliveryException:
                # do not update email / login
                # if for any reason we cannot send email
                can_change = False
            if can_change and self.o_request.website:
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
            return True
        return False
