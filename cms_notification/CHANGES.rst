=========
CHANGELOG
=========

11.0.1.0.2 (2018-08-07)
=======================

**Fixes**

* Fix access to ir.model in listing
    
  In message listing we show info (name, description)
  from the model record referenced by the mail message.

  We now  sudo to grant permission over ir.model
  as this is harmless in this context.


* Fix JS rpc calls to use `this._rpc`

* Relax security for user record
    
  Users must be able to edit their own record
  but this should be narrowed to portal users
  as other kind of users may have different permissions (like employees).
  Anon users are already blocked.


11.0.1.0.1 (2018-04-17)
=======================

**Fixes**

* Adapt to cms_form changes: form_model_key now accepts kw args


11.0.1.0.0 (2018-01-18)
=======================

Upgrade to v11
