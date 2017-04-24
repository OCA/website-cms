.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================
CMS delete content
==================

Basic features for deleting content via frontend.

Features
========

* generic controllers for delete confirmation and delete

    * `/cms/<string:model>/<int:model_id>/delete/confirm`
    * `/cms/<string:model>/<int:model_id>/delete`

* generic template for asking delete confirmation
* new fields and parameters on `website.published.mixin` to handle delete links and redirects
* register your own custom delete confirmation view per-model

    * you can provide a custom delete confirmation view for you model by using a proper id, like: `cms_delete_content.my_model` where as `my_model` matches `my.model` model.

* use `cms_status_message` to show confirmation message for deletion


Usage
=====

Delete button and behavior
--------------------------

To bring the user to delete confirmation page do this in your template::

    <a class="btn btn-danger" t-att-href="object.cms_delete_confirm_url">Delete</a>

This will lead the user to the delete confirmation page, where the user has 2 options:

    * confirm deletion: does a post request to delete controller, accessible directly via `object.cms_delete_url`
    * cancel deletion: bring back to `object.website_url` if present or to HTTP referrer

After deletion the user land on `model.cms_after_delete_url` where `model` is your current model of course.

Customization
-------------

To provide your own deletetion controllers, do this::

    from odoo.addons.cms_delete_content.controllers import DeleteMixin
    from odoo import http

    class CustomDeleteController(http.Controller, DeleteMixin):
        """Controller for handling model deletion."""

        @http.route(
            '/projects/<model("project.project"):main_object>/delete/confirm',
            type='http', auth="user", website=True)
        def delete_confirm(self, main_object, **kwargs):
            return self.handle_delete_confirm(main_object._name, main_object.id, **kwargs)

        @http.route(
            '/projects/<model("project.project"):main_object>/delete',
            type='http', auth="user", website=True, methods=['POST'])
        def delete(self, main_object, **kwargs):
            return self.handle_delete(main_object._name, main_object.id, **kwargs)

Then, you can override

* `_compute_cms_delete_confirm_url` method to change the default delete confirmation url. In this case: `/projects/project.slug-1/delete/confirm`
* `_compute_cms_delete_url` method to change the default delete url. In this case: `/projects/project.slug-1/delete`.
* `cms_after_delete_url` parameter to provide a different url to redirect to after deletion. In this case: `/projects`

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/website-cms/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Simone Orsi <simone.orsi@camptocamp.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
