.. image:: https://img.shields.io/badge/licence-lgpl--3-blue.svg
   :target: http://www.gnu.org/licenses/LGPL-3.0-standalone.html
   :alt: License: LGPL-3

CMS Mixins
==========

* ``cms.security.mixin``


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
