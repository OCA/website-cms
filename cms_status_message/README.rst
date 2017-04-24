.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================
CMS status message
==================

A "status message" is an important message that you want to show to users.

For instance: a user submit a form or does a specific action
and you want to report the status of this action
like "your profile has been updated" or "Your upgrade has been successful.".

This module allows to easily display this kind of messages to your users.

Messages are displayed using Twitter bootstrap alerts.

You can add several messages: they will be displayed one after another.

Usage
=====

Python code
-----------

Set a message:

```python
msg = _('My important message.')
if request.website:
    request.website.add_status_message(msg)
```

By default the message type is `info`.
The title (the label at the beginning of the message) matches the message type:

* 'info': 'Info'
* 'success': 'Success'
* 'danger': 'Error'
* 'warning': 'Warning'


You can change message parameters:

```python
msg = _('Watch out!')
if request.website:
    request.website.add_status_message(msg, mtype='warning', mtitle='Oh no')
```

Messages will be displayed like this:

|preview|

Javascript code
---------------

Dependencies:

```javascript

var msg_tool = require('cms_status_message.tool');
var core = require('web.core');
var _t = core._t;
```

Inject a custom message on the fly:

```javascript
msg = {
    'msg': _t('Item unpublished.'),
    'title': _t('Warning'),
    'type': 'warning'
}
// wipe existing
$('.status_message').remove();

// inject new
$(msg_tool.render_messages(msg))
    .hide()
    .prependTo('main')
    .fadeIn('slow');
```

Add a status message to the session, useful if you want to show the message only after a redirect:

```javascript
var msg =  _t('Contratulations! You made it!.');
var options = {'title': _('My title'), 'dismissible': false};
msg_tool.add_message(msg, options);
```

Customize appereance
--------------------

By default the alert box is added on top of `<main />` content.
If you want to customize this behavior just override or disable `cms_status_message.add_status_message` template.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/website-cms/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

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


.. |preview| image:: ./images/preview.png
