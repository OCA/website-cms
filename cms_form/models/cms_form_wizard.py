# Copyright 2017-2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models
from copy import deepcopy


class CMSFormWizard(models.AbstractModel):
    """Base class for wizards.

    Every wizard is composed by steps.
    Each step can be handled by a different form (see `wiz_configure_steps`).
    Each form must inherit from the main wizard class.
    See also `tests.fake_models.FakeWiz`.
    """
    _name = 'cms.form.wizard'
    _inherit = 'cms.form'
    _form_mode = 'wizard'
    _wiz_name = _name
    form_buttons_template = 'cms_form.wizard_form_buttons'
    # display wizard progress bar?
    wiz_show_progress_bar = True
    # fields declared here will be automatically stored
    # into wizard storage
    # Use `_wiz_step_stored_fields = 'all'` to store them all.
    # You can pass a list of fields if you don't want to store them all.
    _wiz_step_stored_fields = 'all'

    @property
    def form_wrapper_css_klass(self):
        klass = super().form_wrapper_css_klass
        return klass + ' ' + self._wiz_name.replace('.', '_').lower()

    @property
    def _wiz_storage_key(self):
        """Main storage key."""
        return self._wiz_name

    @property
    def _wiz_storage(self):
        return self.request.session

    def wiz_storage_get(self):
        if not self._wiz_storage.get(self._wiz_storage_key):
            # use `deepcopy` to not reference steps' dict
            self._wiz_storage[self._wiz_storage_key] = \
                deepcopy(self.DEFAULT_STORAGE_KEYS)
        return self._wiz_storage[self._wiz_storage_key]

    DEFAULT_STORAGE_KEYS = {
        'steps': {},
        'current': 1,
        'next': None,
        'prev': None,
    }

    def form_init(self, request, main_object=None, page=1, wizard=None, **kw):
        form = super().form_init(request, main_object=main_object, **kw)
        form.wiz_init(page=page, **kw)
        return form

    def wiz_init(self, page=1, **kw):
        steps = self.wiz_configure_steps()
        storage = self.wiz_storage_get()
        for k in steps.keys():
            if k not in storage['steps']:
                # init missing step
                storage['steps'][k] = {}
        current = page
        storage['current'] = current
        _next = None
        if (current + 1) in steps:
            _next = current + 1
        _prev = None
        if (current - 1) in steps:
            _prev = current - 1
        storage['next'] = _next
        storage['prev'] = _prev

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
        except KeyError:
            raise ValueError('Step `%s` does not exists.' % str(step))

    def wiz_current_step(self):
        return self.wiz_storage_get().get('current') or 1

    def wiz_next_step(self):
        return self.wiz_storage_get().get('next')

    def wiz_prev_step(self):
        return self.wiz_storage_get().get('prev')

    def form_next_url(self, main_object=None):
        direction = self.request.form.get('wiz_submit', 'next')
        if direction == 'next':
            step = self.wiz_next_step()
        else:
            step = self.wiz_prev_step()
        if not step:
            # fallback to page 1
            step = 1
        return self._wiz_url_for_step(step, main_object=main_object)

    def _wiz_url_for_step(self, step, main_object=None):
        return '{}/page/{}'.format(self._wiz_base_url(), step)

    def _wiz_base_url(self):
        return '/cms/wiz/{}'.format(self._wiz_name)

    def wiz_save_step(self, values, step=None):
        step = step or self.wiz_current_step()
        storage = self.wiz_storage_get()
        if step not in storage['steps']:
            # safely re-init step
            storage['steps'][step] = {}
        storage['steps'][step].update(values)

    def wiz_load_step(self, step=None):
        step = step or self.wiz_current_step()
        return self.wiz_storage_get()['steps'].get(step) or {}

    def form_after_create_or_update(self, values, extra_values):
        step_values = self._prepare_step_values_to_store(values, extra_values)
        self.wiz_save_step(step_values)

    def _prepare_step_values_to_store(self, values, extra_values):
        values = values.copy()
        values.update(extra_values)
        step_values = {}
        stored_fields = self._wiz_step_stored_fields
        if stored_fields == 'all':
            stored_fields = values.keys()
        for fname in stored_fields:
            if fname in values:
                step_values[fname] = values[fname]
        return step_values
