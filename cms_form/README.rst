.. image:: https://img.shields.io/badge/licence-lgpl--3-blue.svg
   :target: http://www.gnu.org/licenses/LGPL-3.0-standalone.html
   :alt: License: LGPL-3

CMS Form
========

Basic website contents form framework. Allows to define front-end forms for every models in a simple way.

If you are tired of re-defining every time an edit form or a search form for your odoo website,
this is the module you are looking for.

Features
========

* automatic form generation (create, write, search, wizards)
* automatic route generation (create, write, search, wizards)
* automatic machinery based on fields' type:
    * widget rendering
    * field value load (from existing instance or from request)
    * field value extraction (from request)
    * field value write (to existing instance)
* automatic field grouping in fieldsets

* highly customizable
* works with every odoo model
* works also without any model

Usage
=====

Check full documentation inside `doc` folder.


Known issues / Roadmap
======================

* add more tests, especially per each widget and type of field
* provide better widgets for image and file fields in general
* o2m fields: to be tested at all
* move widgets to abstract models too
* search form: generate default search domain in a clever way
* add easy way to switch from horizontal to vertical form
* provide more examples
* x2x fields: allow sub-items creation
* handle api onchanges
* support python expressions into master/slave rules


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/website-cms/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Sponsor
-------

* `Fluxdock.io <https://fluxdock.io>`_.

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
