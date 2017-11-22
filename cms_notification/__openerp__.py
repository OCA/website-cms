# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'CMS notification',
    'summary': """Basic notifications management for your CMS system""",
    'version': '9.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'Camptocamp,Odoo Community Association (OCA)',
    'depends': [
        'cms_form',
        'mail_digest',
        # We need latest fontawesome resources.
        # Use server-tools/9.0/base_fontawesome
        'base_fontawesome',
    ],
    'data': [
        'views/mail_message_subtype_views.xml',
        'templates/assets.xml',
        'templates/help_msg.xml',
        'templates/widget.xml',
        'templates/user_menu.xml',
        'templates/notification_listing.xml',
    ],
}
