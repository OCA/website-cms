# Copyright 2017-2018 Rémy Taymans
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Cms Delete Content Example",
    "summary": """
        Basic content to showcase the CMS delete content""",
    "version": "13.0.1.0.0",
    "license": "LGPL-3",
    "author": "Rémy Taymans, Odoo Community Association (OCA)",
    "depends": ["website", "cms_delete_content"],
    "data": ["data/examples.xml", "data/ir.model.access.csv", "templates/example.xml"],
    "installable": True,
}
