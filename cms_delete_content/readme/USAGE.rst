Delete button and behavior
~~~~~~~~~~~~~~~~~~~~~~~~~~

To add a delete button:

.. code:: html

    <a class="btn btn-danger cms_delete_confirm" t-att-href="object.cms_delete_confirm_url">Delete</a>

When you click on a confirmation dialog pops up.

If you hit ``cancel`` the popup is closed. If you hit submit the item is
deleted and you get redirected to your model's ``cms_after_delete_url``.
By default is ``/``.

**Customization**

Custom per-model delete message
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
