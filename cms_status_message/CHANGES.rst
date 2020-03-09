=========
CHANGELOG
=========

11.0.1.3.0 (2018-08-07)
=======================

**Improvements**

* Get rid of example package

  The example package was there only to show how a message would look like.
  But in real life you want always to verify how they look like
  with your theme styles applied.

  Now we have a new route `/cms/status-message/display-test` to check them.
  `cms_status_message_example` module has been removed.


11.0.1.2.0 (2018-08-07)
=======================

**Improvements**

* Add auto-dimiss option

  By default messages will be auto-dismissed after 8 seconds.
  You can turn this off by setting an ir.config_param like::

    cms_status_message.autodismiss = 0

  You can customize the timeout by setting the key::

    cms_status_message.autodismiss_timeout = 3000  # milliseconds

  Check README for further info.


11.0.1.1.0 (2018-04-22)
=======================

**Improvements**

* Improve JS API

  1. load qweb template on demand
  2. load qweb template only if not loaded yet
  3. use promises for rendering

  We load qweb templates via JS.
  Prior to this change we got 1 request every time,
  on every page load per each template,
  even if we were not using any status message feature.

  Now we load templates only when needed
  and we load them only if not loaded yet,
  lowering page load time a bit :)

  Plus, rendering now returns a promise object so you can chain calls
  and do things when rendering is really finished.


11.0.1.0.0 (2018-01-18)
=======================

Upgrade to v11
