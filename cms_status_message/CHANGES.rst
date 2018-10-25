=========
CHANGELOG
=========


10.0.1.1.0 (2018-05-10)
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


10.0.1.0.0 (2017-01-10)
=======================

* Upgrade to v11