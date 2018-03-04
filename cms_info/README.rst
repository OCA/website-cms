.. image:: https://img.shields.io/badge/licence-lgpl--3-blue.png
   :target: http://www.gnu.org/licenses/LGPL-3.0-standalone.html
   :alt: License: LGPL-3

========
CMS Info
========

Provide basic information for website records / models via `website.published.mixin`.
This module is meant to be used as a base to build your own CMS.

New attributes
--------------

* ``cms_create_url``: lead to create view. By default ``/cms/create/my.model``
* ``cms_search_url``: lead to search view. By default ``/cms/search/my.model``
* ``cms_edit_url`` (computed field): lead to edit view. By default ``/cms/edit/my.model/model_id``

.. note:: No routing provided.
   This attributes provide only basic information on contents' URLs.
   If you use `cms_form` default routes are handled automatically.
   If not, is up to you to provide your own routes to handle them.


Permission and extra information
--------------------------------

* ``record.cms_is_owner()``: current user is the owner of the record?
* ``record.cms_can_edit()``: current user can edit this record?
* ``record.cms_can_publish()``: current user can publish this record?
* ``record.cms_can_delete()``: current user can delete this record?
* ``model.cms_can_create()``: current user can create a new record?


Info all in one
---------------

When you build CMS UIs you need all those info at once.
This module provides also an helper method `cms_info()`
that gives you back a dictionary containing:

* `is_owner`: True/False,
* `can_edit`: True/False,
* `can_create`: True/False,
* `can_publish`: True/False,
* `can_delete`: True/False,
* `create_url`
* `edit_url`
* `delete_url`


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/website-cms/issues>`_.
In case of trouble, please check there if your issue has already been reported.


Credits
=======

Contributors
------------

* Simone Orsi <simone.orsi@camptocamp.com>


Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
