=========
CHANGELOG
=========


11.0.1.6.2 (2018-08-21)
=======================

**Fixes**

* Date widget JS datepicker default date regression

  Make sure we use today date unless specified otherwise.


11.0.1.6.1 (2018-08-07)
=======================

**Fixes**

* Date widget JS datepicker options custom

  You can now override all the options of the datepicker via `data`.
  For instance::

      def form_get_widget(self, fname, field, **kw):
          """Customize datepicker."""
          if fname == 'date':
              kw['data'] = {
                  'minDate': '2018-01-01'
              }
          return super().form_get_widget(fname, field, **kw)


11.0.1.6.0 (2018-07-25)
=======================

**Improvements**

* Add `:float` marshaller

  You can now use `$foo:float` as field name to cast value to float.

* Hidden input respect field type value

  Hidden input values pass through requests as chars.
  This means that any m2o or selection field with integer/float values
  won't be really happy on create/write.

  Now we rely on request marshallers to convert those values
  to correct values based on field type.

  NOTE: this is the preliminary step for adopting marshallers
  for all field types/widgets when needed.


**Fixes**

* Fix `safe_to_date` to make form extractor happy

  Form extractor ignores non required fields if their values is `None`.
  In the case of the date field, the util was returning `False`
  even if the value was not submitted, leading to an ORM error
  whenever the missing field was required.

  Now we return `None` and let the extractor deal with proper values
  and validation.

**Coverage**

* Test field wrapper rendering
* Test css klass methods
* Test `get_widget`
* Test conversion of no value
* Test fieldsets rendering

  Make sure fieldsets are not rendered if they have no fields.

* Allow to skip HttpCase on demand

  Super-useful when you use pytest which does not support them.

* Add basic tests for widget
* Add test for hidden widget
* Add test for char widget


11.0.1.5.2 (2018-07-12)
=======================

**Fixes**

* Fix ordering w/ `groups` protected fields

  If `groups` attribute was assigned to a field
  it made fields ordering crash as the field is not there
  when groups are not satisfied

* Fix selection widget to handle integer values

  `fields.Selection` can hold both strings and integer values.
  Till the value was not converted automatically
  and using selection fields w/ integer values was a bit complex
  as you had to convert it yourself or use a str selection field.

  Now the widget inspects selection options
  and converts request value accordingly.


11.0.1.5.1 (2018-07-09)
=======================

**Fixes**

* Fix regression fields ordering + hidden

  When calling `form_fields` w/ hidden=True/False
  the order of the fields was not respected anymore.

  This a regression from commit 56b37ca


11.0.1.5.0 (2018-07-06)
=======================

**Improvements**

* Handle hidden input automatically

  You can now specify `_form_fields_hidden = ('foo', )`
  to get hidden inputs. All fields declared here
  will be rendered as `<input type="hidden" />`.


11.0.1.4.4 (2018-07-04)
=======================

**Fixes**

* Search form: fix default URL py3 compat


11.0.1.4.3 (2018-07-04)
=======================

**Fixes**

* Be defensive on error block render (do not fail if none)
* Widgets: fix missing `required` attribute
* Search form: discard empty strings in search domain
* Cleanup controller render values

  When you submit a form and there's an error Odoo will give you back
  all submitted values into `kw` but:

  1. we don't need them since all values are encapsulated
     into form.form_render_values
     and are already accessible on each widget

  2. this can break website rendering because you might have fields
     w/ a name that overrides a rendering value not related to a form.
     Most common example: field named `website` will override
     odoo record for current website.


11.0.1.4.2 (2018-05-31)
=======================

**Improvements**

* Search form: use safe default for pager url
* Search form: support quick domain rules via `_form_search_domain_rules`


11.0.1.4.1 (2018-04-29)
=======================

**Docs**

* Move documentation from README to `doc` folder


11.0.1.4.0 (2018-04-27)
=======================

**Improvements**

* Include wizard name in form wrapper klass
* Add request marshallers and tests
* Search form: pass `pager` as render value

  This change is to facilitate templates that need a pager
  to generate page metadata (like links prev/next).

  A good use case is the SEO friendly `website_canonical_url`.

* Rely on `cms_info` for permission and URLs


**Fixes**

* Fix `fake_session` helper in form tests common


11.0.1.3.1 (2018-04-22)
=======================

**Improvements**

* Wizard: ease customization of stored values

  To customize stored values you can override `_prepare_step_values_to_store`


11.0.1.3.0 (2018-04-17)
=======================

**Improvements**

* Add wizard support to easily create custom wizards


11.0.1.2.1 (2018-04-13)
=======================

**Fixes**

* Fix search form regression on permission check

  In 32a662e I've moved permission check from controller to form
  but I missed the bypass for search forms.


11.0.1.2.0 (2018-04-09)
=======================

**Improvements**

* Add error msg block for validation errors right below field
* Support multiple values for same field

  In the input markup you can set the field name as `$fname:list`.

  This will make the form transform submitted values as a list.

  Example::

      <input name="foo:list" type="checkbox" value="1" />
      <input name="foo:list" type="checkbox" value="2" />
      <input name="foo:list" type="checkbox" value="3" />

  Will be translated to: `{'foo': [1, 2, 3]}`


* Add `lock copy paste` option

  You can now pass `lock_copy_paste` to widget init via `css_klass` arg
  to set an input/text w/ copy/paste disabled.

  Example::

      def form_get_widget(self, fname, field, **kw):
          """Disable copy paste on `foo`."""
          if fname == 'foo':
              kw['css_klass'] = 'lock_copy_paste'
          return super().form_get_widget(fname, field, **kw)


* `form_get_widget` pass keyword args to ease customization
* Form controller: better HTTP status for redirect (303) and no cache
* Improve custom attributes override
* Move `check_permission` to form

  You can now customize permission check on each form.
  Before this change you had to override the controller to gain control on it.


**Fixes**

* Fix required attr on boolean widget (was not considered)
* `_form_create` + `_form_write` use a copy of values to avoid pollution by Odoo
* Fix handling of forms w/ no form_model
  (some code blocks were relying on `form_model` to be there)


11.0.1.1.1 (2018-03-26)
=======================

**Fixes**

* Fix date widget: default today only if empty


11.0.1.1.0 (2018-03-26)
=======================

**Improvements**

* Delegate field wrapper class computation to form
* Add vertical fields option
* Add multi value widget for search forms
* Improve date widget: allow custom default today

**Fixes**

* Fix fieldset support for search forms
* Fix date search w/ empty value
* Fix json params rendering on widgets


11.0.1.0.4 (2018-03-23)
=======================

**Improvements**

* Ease override of JSON info
* Add fieldsets support
* cms_form_example: add fieldsets forms


11.0.1.0.3 (2018-03-21)
=======================

**Improvements**

* Form controller: main_object defaults to empty recordset

**Fixes**

* Fix x2m widget value comparison
* Fix x2m widget load default value empt^^
