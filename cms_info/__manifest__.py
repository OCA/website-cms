# Copyright 2018 Simone Orsi - Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "CMS info",
    "summary": """A set of basic information needed on all published records.""",
    "version": "13.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/OCA/website-cms",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    # TODO: think about make cms stuff independent from `website`.
    # If you want to use these features in portal only it shouldn't be required
    # to install `website`.
    "depends": ["website"],
}
