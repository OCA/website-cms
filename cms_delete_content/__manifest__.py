# Copyright 2017-2018 Camptocamp - Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "CMS delete content",
    "summary": """
        Basic features for handling content deletion via frontend.""",
    "version": "13.0.1.0.0",
    "license": "LGPL-3",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "depends": ["website", "cms_info", "cms_status_message"],
    "data": ["templates/assets.xml", "templates/delete_confirm.xml"],
    "installable": True,
}
