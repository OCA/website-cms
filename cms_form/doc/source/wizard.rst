Wizards
=======

Basics
------

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
