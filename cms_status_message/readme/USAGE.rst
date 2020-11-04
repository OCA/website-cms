Python code
~~~~~~~~~~~

Set a message:

.. code:: python

    msg = _('My important message.')
    if request.website:
        request.website.add_status_message(msg)

By default the message type is ``info``. The title (the label at the
beginning of the message) matches the message type:

-  'info': 'Info'
-  'success': 'Success'
-  'danger': 'Error'
-  'warning': 'Warning'

You can change message parameters:

.. code:: python

    msg = _('Watch out!')
    if request.website:
        request.website.add_status_message(msg, type_='warning', title='Oh no')

Messages will be displayed like this:

.. image:: ./images/preview.png

Autodismiss
~~~~~~~~~~~

By default messages will be auto-dismissed after 8 seconds.
You can turn this off by setting an ir.config_param like::

    cms_status_message.autodismiss = 0

You can customize the timeout by setting the key::

    cms_status_message.autodismiss_timeout = 3000  # milliseconds


You can also customize this on demand when you create the message:


.. code:: python

    msg = _('I will disappear more slowly')
    options = {'autodismissTimeout': 10000}
    if request.website:
        request.website.add_status_message(msg, dismiss_options=options)


Javascript code
~~~~~~~~~~~~~~~

Dependencies:

.. code:: javascript


    var msg_tool = require('cms_status_message.tool');
    var core = require('web.core');
    var _t = core._t;

Inject a custom message on the fly:

.. code:: javascript

    msg = {
        'msg': _t('Item unpublished.'),
        'title': _t('Warning'),
        'type': 'warning'
    }
    msg_tool.render_messages(msg).then(function(html) {
        // wipe existing
        $('.status_message').remove();
        // inject new
        $(html).hide().prependTo('#wrap').fadeIn('slow');
    });


Add a status message to the session, useful if you want to show the
message only after a redirect:

.. code:: javascript

    var msg =  _t('Contratulations! You made it!.');
    var options = {'title': _('My title'), 'dismissible': false};
    msg_tool.add_message(msg, options);

Customize appereance
~~~~~~~~~~~~~~~~~~~~

By default the alert box is added on top of ``<main />`` content. If you
want to customize this behavior just override or disable
``cms_status_message.add_status_message`` template.


Test your theme look and feel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Go to `/cms/status-message/display-test` to see how messages will look like
when your theme is applied.
