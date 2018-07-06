Form advanced
=============

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


Hidden fields
-------------

You might want to use `<input type="hidden" />` for certain fields.
To achieve this just use `_form_fields_hidden`:

.. code-block:: python

    class PartnerForm(models.AbstractModel):

        _name = 'cms.form.res.partner'
        _inherit = 'cms.form'
        _form_model = 'res.partner'
        _form_model_fields = ('name', 'type', 'foo')
        _form_fields_hidden = ('foo', )

Field "foo" will be rendered at the top of the form markup with an hidden input.
For create forms, you might want to pass a default value to it, like:

    
.. code-block:: python
    
    class PartnerForm(models.AbstractModel):
        [...]
        def form_load_defaults(self, main_object=None, request_values=None):
            defaults = super().form_load_defaults(
                main_object=main_object, request_values=request_values
            )
            defaults['foo'] = 'I can pass a default value here'
            return defaults
