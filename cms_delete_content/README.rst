.. image:: https://img.shields.io/badge/licence-lgpl--3-blue.svg
   :target: http://www.gnu.org/licenses/LGPL-3.0-standalone.html
   :alt: License: LGPL-3

==================
CMS delete content
==================

Basic features for deleting content via frontend.

Features
--------

-  register your own custom delete confirmation view per-model
-  use ``cms_status_message`` to show confirmation message for deletion
-  generic template for asking delete confirmation
-  new fields and parameters on ``website.published.mixin`` to handle
   delete links and redirects

Usage
-----

Delete button and behavior
~~~~~~~~~~~~~~~~~~~~~~~~~~

To add a delete button:

.. code:: html

    <a class="btn btn-danger cms_delete_confirm" t-att-href="object.cms_delete_confirm_url">Delete</a>

When you click on a confirmation dialog pops up.

If you hit ``cancel`` the popup is closed. If you hit submit the item is
deleted and you get redirected to your model's ``cms_after_delete_url``.
By default is ``/``.

Customization
-------------

Custom per-model delete messge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    class MyModel(models.Model):
        _inherit = "my.model"

        @api.multi
        def msg_content_delete_confirm(self):
            self.ensure_one()
            return _('Are you sure you want to delete "%s"?.') % self.name

Custom "after delete URL"
~~~~~~~~~~~~~~~~~~~~~~~~~

When you are viewing a content and you delete it you want to be
redirected to some other place.

By default you get redirected to the root of the website.

To change this behavior just override the attribute in your model
declaration:

.. code:: python

    class MyModel(models.Model):
        _inherit = "my.model"

        cms_after_delete_url = '/foo'

Note: if you want to customize it on demand for particular pages, or you
are deleting an item from another page (like a management page) you can
pass ``?redirect=`` in the url, like:

.. code:: html

    <a class="btn btn-danger cms_delete_confirm" t-attf-href="#{object.cms_delete_confirm_url}?redirect=">Delete</a>

Custom global delete confirm message appeareance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: xml

    <template id="delete_confirm" inherit_id="cms_delete_content.delete_confirm">

        <xpath expr="//h4[@id='delete_confirm']" position="replace">
            <h1 t-esc="main_object.msg_content_delete_confirm()">I want it bigger!</h1>
        </xpath>

    </template>


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/website-cms/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smash it
by providing detailed and welcomed feedback.


Credits
=======

Contributors
------------

-  Simone Orsi simone.orsi@camptocamp.com

Maintainer
----------


.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org


This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization
whose mission is to support the collaborative development of Odoo
features and promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
