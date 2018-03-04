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

Create / Edit form
------------------

Just inherit from ``cms.form`` to add a form for your model. Quick example for partner:

.. code-block:: python

    class PartnerForm(models.AbstractModel):

        _name = 'cms.form.res.partner'
        _inherit = 'cms.form'
        _form_model = 'res.partner'
        _form_model_fields = ('name', 'country_id')
        _form_required_fields = ('name', 'country_id')


In this case you'll have form with the following characteristics:

* works with ``res.partner`` model
* have only ``name`` and ``country_id`` fields
* both fields are required (is not possible to submit the form w/out one of those values)

Here's the result:

|preview_create|
|preview_edit|

The form will be automatically available on these routes:

* ``/cms/create/res.partner`` to create new partners
* ``/cms/edit/res.partner/1`` edit existing partners (partner id=1 in this case)

NOTE: default generic routes work if the form's name is ``cms.form.`` + model name, like ``cms.form.res.partner``.
If you want you can easily define your own controller and give your form a different name,
and have more elegant routes like ```/partner/edit/partner-slug-1``.
Take a look at `cms_form_example <../cms_form_example>`_.

By default, the form is rendered as an horizontal twitter bootstrap form, but you can provide your own templates of course.
By default, fields are ordered by their order in the model's schema. You can tweak it using ``_form_fields_order``.


Form with extra control fields
------------------------------

Imagine you want to notify the partner after its creation but only if you really need it.

The form above can be extended with extra fields that are not part of the ``_form_model`` schema:

.. code-block:: python

    class PartnerForm(models.AbstractModel):

        _name = 'cms.form.res.partner'
        _inherit = 'cms.form'
        _form_model = 'res.partner'
        _form_model_fields = ('name', 'country_id', 'email')
        _form_required_fields = ('name', 'country_id', 'email')

        notify_partner = fields.Boolean()

        def form_after_create_or_update(self, values, extra_values):
            if extra_values.get('notify_partner'):
                # do what you want here...

``notify_partner`` will be included into the form but it will be discarded on create and write.
Nevertheless you can use it as a control flag before and after the record has been created or updated
using the hook ``form_after_create_or_update``, as you see in this example.


Form with fieldsets and tabs
----------------------------

You want to group fields into meaningful groups. You can use fieldsets:

.. code-block:: python

    class PartnerForm(models.AbstractModel):

        _name = 'cms.form.res.partner'
        _inherit = 'cms.form'
        _form_model = 'res.partner'
        _form_model_fields = ('name', 'country_id', 'email')
        _form_required_fields = ('name', 'country_id', 'email')
        _form_fieldsets = [
            {
                'id': 'main',
                'title': 'Main',
                'fields': [
                    'name',
                    'email',
                ],
            },
            {
                'id': 'secondary',
                'title': 'Secondary',
                'fields': [
                    'country_id',
                    'notify_partner',
                ],
            },
        ]

        notify_partner = fields.Boolean()

|preview_fieldsets|


If you want fieldsets to be displayed as tabs, just override this option:

.. code-block:: python

    class PartnerForm(models.AbstractModel):

        _name = 'cms.form.res.partner'
        _inherit = 'cms.form'
        _form_fieldsets = [...]
        _form_fieldsets_display = 'tabs'


|preview_tabbed|


Search form
-----------

Just inherit from ``cms.form.search`` to add a form for your model. Quick example for partner:

.. code-block:: python

    class PartnerSearchForm(models.AbstractModel):
        """Partner model search form."""

        _name = 'cms.form.search.res.partner'
        _inherit = 'cms.form.search'
        _form_model = 'res.partner'
        _form_model_fields = ('name', 'country_id', )
        _form_fields_order = ('country_id', 'name', )


|preview_search|

The form will be automatically available at: ``/cms/search/res.partner``.

NOTE: default generic routes work if the form's name is ```cms.form.search`` + model name, like ``cms.form.search.res.partner``.
If you want you can easily define your own controller and give your form a different name,
and have more elegant routes like ``/partners``.
Take a look at `cms_form_example`.


Wizards
-------

Just inherit from ``cms.form.wizard`` and describe your steps. Quick example:

.. code-block:: python

    class FakeWiz(models.AbstractModel):
        """A wizard form."""

        _name = 'fake.wiz'
        _inherit = 'cms.form.wizard'
        _wiz_name = _name

        def wiz_configure_steps(self):
            return {
                1: {'form_model': 'fake.wiz.step1.country'},
                2: {'form_model': 'fake.wiz.step2.partner'},
                3: {'form_model': 'fake.wiz.step3.partner'},
            }


    class FakeWizStep1Country(models.AbstractModel):

        _name = 'fake.wiz.step1.country'
        _inherit = 'fake.wiz'
        _form_model = 'res.country'
        _form_model_fields = ('name', )


    class FakeWizStep2Partner(models.AbstractModel):

        _name = 'fake.wiz.step2.partner'
        _inherit = 'fake.wiz'
        _form_model = 'res.partner'
        _form_model_fields = ('name', )


    class FakeWizStep3Partner(models.AbstractModel):

        _name = 'fake.wiz.step3.partner'
        _inherit = 'fake.wiz'
        _form_model = 'res.partner'
        _form_model_fields = ('category_id', )



The form will be automatically available at: ``/cms/wiz/fake.wiz/page/1``.

As you see each step can use its own form.
In this case on the 1st page the user will deal with countries,
then on the 2nd step with the name of the partner
and on the last step only with partner category.

The wizard machinery will handle session storage and navigation 
between steps automatically.


Master / slave fields
---------------------

A typical use case nowadays: you want to show/hide fields based on other fields' values.
For the simplest cases you don't have to write a single line of JS. You can do it like this:

.. code-block:: python

    class PartnerForm(models.AbstractModel):

        _name = 'cms.form.res.partner'
        _inherit = 'cms.form'
        _form_model = 'res.partner'
        _form_model_fields = ('name', 'type', 'foo')

        def _form_master_slave_info(self):
            info = self._super._form_master_slave_info()
            info.update({
                # master field
                'type':{
                    # actions
                    'hide': {
                        # slave field: action values
                        'foo': ('contact', ),
                    },
                    'show': {
                        'foo': ('address', 'invoice', ),
                    }
                },
            })
            return info

Here we declared that:

* when `type` field is equal to `contact` -> hide `foo` field
* when `type` field is equal to `address` or `invoice` -> show `foo` field


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

.. |preview_create| image:: ./images/cms_form_example_create_partner.png
.. |preview_edit| image:: ./images/cms_form_example_edit_partner.png
.. |preview_search| image:: ./images/cms_form_example_search.png
.. |preview_fieldsets| image:: ./images/cms_form_example_fieldsets.png
.. |preview_tabbed| image:: ./images/cms_form_example_tabbed.png
