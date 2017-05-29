.. image:: https://img.shields.io/badge/licence-lgpl--3-blue.svg
   :target: http://www.gnu.org/licenses/LGPL-3.0-standalone.html
   :alt: License: LGPL-3

CMS mixin
==========

* ``cms.security.mixin``
* ``cms.orderable.mixin``
* ``cms.coremetadata.mixin``
* ``cms.content.mixin``
* ``cms.parent.mixin``


Security mixin
--------------

Implements basic security features on your model. Provides:

* only owner can edit or delete
* only owner can view if not published
* only published items are visible by other users or anonymous users
* you can grant view/edit permissions by using `read_group_ids` and `write_group_ids`
* the model controller will raise `NotFound` if current user cannot see the item
  **before** template rendering (right now you get an access error
  only if you access a field of the object)

All of this is automatically activated by setting the flag `_auto_security_policy = True`.
By default is `False` as you might want to implement your own security policy.

Usage:

.. code:: python

    class SecuredModel(models.Model):
        _name = 'testmodel.secured'
        _inherit = [
            'website.published.mixin',
            'cms.security.mixin',
        ]
        # generate security automatically
        _auto_security_policy = True


Orderable mixin
---------------

Implements basic ordering features:

* order model by `sequence desc` by default
* last created item has always higher sequence

Usage:

.. code:: python

    class OrderableModel(models.Model):
        _name = 'testmodel.orderable'
        _inherit = [
            'cms.orderable.mixin',
        ]


Coremetadata mixin
------------------

Implements basic core metadata features:

* exposes create/write fields:

    `create_uid`, `write_uid`, `create_date`, `write_date`

  so that you can use them in backend forms to show important info

* adds new fields:

    * `published_uid` to track who published an item
    * `published_date` to track when an item has been published

Usage:

.. code:: python

    class CoremetadataModel(models.Model):
        _name = 'testmodel.coremetadata'
        _inherit = [
            'website.published.mixin',
            'cms.orderable.mixin',
        ]


Content mixin
-------------

Implements basic website content features:

* the following mixin are already implemented:

    * ``website.published.mixin``
    * ``cms.coremetadata.mixin``
    * ``cms.orderable.mixin``

* adds basic fields:

    * `name` defines content's name and "sluggified" in URL
    * `description` brief description of the content
    * `body` to contain HTML content

* generate basic URL: just provide a `cms_url_prefix` attribute
  to have an URL like `myodoo.com/contents/bla-1`.

Usage:

.. code:: python

    class ContentModel(models.Model):
        _name = 'testmodel.content'
        _inherit = [
            'cms.content.mixin',
        ]
        cms_url_prefix = '/contents/'


Parent mixin
------------

Implements basic website hierarchy features:

* parent / children relations without need to re-define relation per each model

* constrain to avoid recursive parent of parent relation

* helper method for action to open children list in backend

* `hierarchy` method to list the full hierarchy of an item

* `name_get` overide to include - on demand - the full hierarchy path on an item

* `get_listing` method to list all descendant items

Usage:

.. code:: python

    class ParentModel(models.Model):
        """A test model that implements `cms.parent.mixin`."""

        _name = 'testmodel.parent'
        _description = 'cms_mixin: parent test model'
        _inherit = [
            'cms.parent.mixin',
        ]
        name = fields.Char()


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/website-cms/issues>`_.
In case of trouble, please check there if your issue has already been reported.


Credits
=======

Contributors
------------

* Simone Orsi at Camptocamp


Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
