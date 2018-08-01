# Copyright 2018 Simone Orsi - Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import http
from odoo.http import request


class Toolbar(http.Controller):

    # TODO: use POST method
    @http.route([
        '/cms/toolbar/action/state',
    ], type='json', auth='user', website=True)
    def toolbar_action_state(
            self, rec_id=None, model=None,
            transition=None, old_state=None, **kw):
        assert rec_id and model and transition and old_state
        Model = request.env[model]
        record = Model.browse(int(rec_id))
        self._validate_action(record, transition)
        result = self._get_result(record, transition)
        try:
            record.write(result.pop('write_values'))
            result['ok'] = True
            if kw.get('reload'):
                # TODO: compress
                result['html'] = record.cms_render_toolbar()
        except Exception as err:
            result['ok'] = False
            result['error'] = str(err)
        return result

    def _validate_action(self, record, transition):
        # TODO: we support only these transitions ATM
        assert transition in ('publish', 'unpublish')

    def _get_result(self, record, transition):
        vals = {
            'transition': transition,
            'next_transition':
                'unpublish' if transition == 'publish' else 'publish',
            'new_state':
                'published' if transition == 'publish' else 'unpublished',
            'old_state':
                'unpublished' if transition == 'publish' else 'unpublished',
            'write_values': {
                'website_published': transition == 'publish',
            }
        }
        return vals
