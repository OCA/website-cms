# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from copy import deepcopy

from odoo import fields, models

from .fields import Serialized


class CMSFormWizard(models.AbstractModel):
    """Base class for wizards.

    Every wizard is composed by steps.
    Each step can be handled by a different form (see `wiz_configure_steps`).
    Each form must inherit from the main wizard class.
    See also `tests.fake_models.FakeWiz`.
    """

    _name = "cms.form.wizard"
    _description = "CMS Form wizard"
    _inherit = "cms.form"
    _wiz_name = _name
    form_buttons_template = fields.Char(
        form_tech=True, default="cms_form.wizard_form_buttons"
    )
    # display wizard progress bar?
    form_show_progress_bar = fields.Boolean(form_tech=True, default=True)
    # Fields declared here will be automatically stored
    # into wizard storage
    # Use `form_step_store_all_fields = True` to store them all.
    # You can pass a list of fields if you don't want to store them all.
    form_step_stored_fields = Serialized(form_tech=True, default=[])
    form_step_store_all_fields = fields.Boolean(form_tech=True, default=True)
    form_reset = fields.Boolean(form_tech=True, default=False)

    def _is_wiz_main_model(self):
        return self._name == self._wiz_name

    def _get_form_mode(self):
        return "wizard"

    @property
    def form_wrapper_css_klass(self):
        klass = super().form_wrapper_css_klass
        return klass + " " + self._wiz_name.replace(".", "_").lower()

    @property
    def _wiz_storage_key(self):
        """Main storage key."""
        return self._wiz_name

    @property
    def _wiz_storage(self):
        return self.o_request.session

    def wiz_storage_get(self):
        self._wiz_storage_prepare()
        storage = self._wiz_storage[self._wiz_storage_key]
        if "steps" in storage:
            # Depending of the type of session storage data might be serialized.
            # When this happens steps keys might be converted to strings.
            # Ensure we always get integers.
            storage["steps"] = {int(k): v for k, v in storage["steps"].items()}
        return storage

    def _wiz_storage_prepare(self, reset=False):
        if not self._wiz_storage.get(self._wiz_storage_key) or reset:
            # use `deepcopy` to not reference steps' dict
            self._wiz_storage[self._wiz_storage_key] = deepcopy(
                self.DEFAULT_STORAGE_KEYS
            )

    def wiz_storage_set(self, storage):
        self.o_request.session.update({self._wiz_storage_key: storage})
        # Important: ensure the session is stored (will be flagged as dirty)
        # Mandatory since v16 when storing nested objs.
        self.o_request.session.touch()

    DEFAULT_STORAGE_KEYS = {
        "steps": {},
        "current": 1,
        "next": None,
        "prev": None,
    }

    def form_init(self, request, main_object=None, page=1, wizard=None, **kw):
        form = super().form_init(request, main_object=main_object, **kw)
        if form.form_reset:
            form._wiz_storage_prepare(reset=True)
            form.form_reset = False
        form.wiz_init(page=page, **kw)
        return form

    def wiz_init(self, page=1, **kw):
        steps = self.wiz_configure_steps()
        storage = self.wiz_storage_get()
        for k in steps.keys():
            if k not in storage["steps"]:
                # init missing step
                storage["steps"][k] = {}
        current = page
        storage["current"] = current
        _next = None
        if (current + 1) in steps:
            _next = current + 1
        _prev = None
        if (current - 1) in steps:
            _prev = current - 1
        storage["next"] = _next
        storage["prev"] = _prev

    @property
    def wiz_steps(self):
        return list(self.wiz_configure_steps().keys())

    def wiz_configure_steps(self):
        """Configure wizard steps.

        Each step can use a different form, for instance:

        return {
            1: {
                'form_model': 'form.a',
                'title': 'Step 1',
                'description': 'Preliminary info',
            },
            2: {
                'form_model': 'form.b',
                'title': 'Step 2',
            },
            3: {
                'form_model': 'form.c',
                'title': 'Step 3',
                'description': 'Foo',
            },
        }
        """
        return {}

    def wiz_get_step_info(self, step):
        step = int(step)
        try:
            return self.wiz_configure_steps()[step]
        except KeyError as e:
            raise ValueError("Step `%s` does not exists." % str(step)) from e

    def wiz_current_step(self):
        return self.wiz_storage_get().get("current") or 1

    def wiz_next_step(self):
        return self.wiz_storage_get().get("next")

    def wiz_prev_step(self):
        return self.wiz_storage_get().get("prev")

    def form_next_url(self, main_object=None):
        direction = self.request.form.get("wiz_submit", "next")
        if direction == "next":
            step = self.wiz_next_step()
        else:
            step = self.wiz_prev_step()

        main_object = main_object or self.main_object
        if (
            main_object
            and "url" in main_object._fields
            and self.is_final_step_process()
        ):
            return main_object.url
        if not step:
            # fallback to page 1
            step = 1
        return self._wiz_url_for_step(step, main_object=main_object)

    def _wiz_url_for_step(self, step, main_object=None):
        return "{}/page/{}".format(self._wiz_base_url(), step)

    def _wiz_base_url(self):
        return "/cms/wiz/{}".format(self._wiz_name)

    def wiz_save_step(self, values, step=None):
        step = step or self.wiz_current_step()
        storage = self.wiz_storage_get()
        if step not in storage["steps"]:
            # safely re-init step
            storage["steps"][step] = {}

        storage["steps"][step].update(values)
        self.wiz_storage_set(storage)

    def wiz_load_step(self, step=None):
        step = step or self.wiz_current_step()
        return self.wiz_storage_get()["steps"].get(step) or {}

    def wiz_load_steps(self, steps=None):
        """Load all steps data merged together."""
        data = self.wiz_storage_get()["steps"]
        steps = steps or data.keys()
        res = {}
        for step in steps:
            res.update(data.get(step, {}))
        return res

    def form_after_create_or_update(self, values, extra_values):
        step_values = self._prepare_step_values_to_store(values, extra_values)
        self.wiz_save_step(step_values)
        if self.is_final_step_process():
            # Wipe session data when done
            self._wiz_storage_prepare(reset=True)

    def is_final_step_process(self):
        # Helper method to determine if the submot action is the last one
        return self.request.form.get("wiz_submit") == "process"

    def _prepare_step_values_to_store(self, values, extra_values):
        values = values.copy()
        values.update(extra_values)
        step_values = {}
        stored_fields = self.form_step_stored_fields
        if not stored_fields and self.form_step_store_all_fields:
            stored_fields = values.keys()
        for fname in stored_fields:
            if fname in values:
                step_values[fname] = values[fname]
        return step_values

    # TODO: tests
    def form_load_defaults(self, main_object=None, request_values=None):
        # Override to load values from the storage
        if self._is_wiz_main_model():
            # Do not load anything if we are initializing the main wiz model
            return {}
        defaults = super().form_load_defaults(
            main_object=main_object, request_values=request_values
        )
        request_values = request_values or {}
        step_values = self.wiz_load_step()
        if step_values:
            for fname in self.form_fields_get().keys():
                if fname in request_values:
                    # req value has precedence
                    continue
                if fname in step_values:
                    defaults[fname] = step_values[fname]
        return defaults
