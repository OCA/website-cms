# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'CMS notification',
    'summary': """Basic notifications management for your CMS system""",
    'version': '11.0.1.0.3',
    'license': 'LGPL-3',
    'author': 'Camptocamp,Odoo Community Association (OCA)',
    'depends': [
        'cms_form',
        'mail_digest',
    ],
    'data': [
        'security/notification_permission.xml',
        'views/mail_message_subtype_views.xml',
        'templates/assets.xml',
        'templates/help_msg.xml',
        'templates/widget.xml',
        'templates/user_menu.xml',
        'templates/notification_listing.xml',
    ],
}
