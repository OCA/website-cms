=========
CHANGELOG
=========

11.0.1.1.0 (2018-07-06)
=======================

**Improvements**

* Delegate render values to model method

  Delegate all render values to  `_cms_toolbar_values`
  so that you can take full controll of what to show w/out
  hacking too much the base template.


**Fixes**

* Fix create button check

  Solved to issues:

  * `right-actions` box was rendered only if `create_url` was satisfied
      making impossible to add more actions unrelated to it

  * use `show_create` as well to display the button or not


11.0.1.0.1 (2018-07-04)
=======================

**Fixes**

* Toolbar: do not render for anon users


11.0.1.0.0 (2018-04-29)
=======================

* Initial release
