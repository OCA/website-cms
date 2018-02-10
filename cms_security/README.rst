.. image:: https://img.shields.io/badge/licence-lgpl--3-blue.svg
   :target: http://www.gnu.org/licenses/LGPL-3.0-standalone.html
   :alt: License: LGPL-3

============
CMS security
============

Implements basic security features on your model.

Features
========

It provides a ``cms.security.mixin``
that gives your models the following security behavior:

* only owner can edit or delete
* only owner can view if not published
* only published items are visible by other users or anonymous users

Additionally:

* you can grant view/edit permissions by using ``read_group_ids`` and ``write_group_ids``


Advanced controller security
----------------------------

By default Odoo raises ``503 Forbidden`` access error
only if you access a field of the record.

`503` is not the perfect status in this case
because it tells you that a record w/ that id in the route exists.

A record that is not published should be NOT found in any case.

This module override the standard model converter to raise ``404 NotFound``
if current user cannot see the item **before** template rendering.


Developer control
-----------------

All of the above features are automatically activated
by setting the flag ``_cms_auto_security_policy = True``.
By default is `False` as you might want to implement your own security policy.

The rules are create only if this flag is turned on and the advanced controller
will check for permissions only if the model inherits from ``CMSSecurityMixin``.


Usage
=====

To secure your model, all you have to do is this:

.. code:: python

    class SecuredModel(models.Model):
        _name = 'my.secure.model'
        _inherit = [
            'website.published.mixin',
            'cms.security.mixin',
        ]
        # generate security automatically
        _cms_auto_security_policy = True


Add your tests easily
---------------------

All the above features are 100% covered with tests.
Furthermore, to ease your duty when adding security tests for your models
you can inherit from the base test cases defined in this module.

To test your ACL + RR:


.. code:: python

   import odoo.tests.common as test_common
   from odoo.cms_security.test.base import BasePermissionTestCase


   class TestSecurity(BasePermissionTestCase, test_common.SavepointCase):
       """All tests come from `BasePermissionTestCase`."""

       at_install = False
       post_install = True

       @property
       def model(self):
           return self.env['my.secure.model']


To test that your controllers work as you expect:

.. code:: python

   import odoo.tests.common as test_common
   from odoo.cms_security.test.base import BaseSecureConverterTestCase


   class SecureConverterTestCase(BaseSecureConverterTestCase,
                                 test_common.SavepointCase):
       """All tests come from `BaseSecureConverterTestCase`."""

       at_install = False
       post_install = True

       @property
       def model(self):
           return self.env['my.secure.model']


Batteries not included
----------------------

This module is a base module
to ease implementation of your own models' security.
It **does not** provide any new model or view (nor backend nor frontend).


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/website-cms/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.


Credits
=======

Contributors
------------

* Simone Orsi <simone.orsi@camptocamp.com>

Do not contact contributors directly about support or help with technical issues.


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
