=========
CHANGELOG
=========


11.0.1.0.2 (2018-04-17)
=======================

**Fix**

* Fix controller: form_model_key now accepts kw args


11.0.1.0.1 (2018-04-09)
=======================

**Fix**

* Fix validators names

  `form_validate_email` and `form_validate_vat` were mispelled
  as they should start w/ `_`. There was no integration test
  for them so their single unit tests were passing.



11.0.1.0.0 (2018-02-12)
=======================

* Initial release
