# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp import http
from openerp import _
from openerp.http import request
import werkzeug


class DeleteMixin(object):

    def get_template_key(self, main_object):
        # lookup for content specific template
        tmpl = request.env.ref(
            'cms_delete_content.{}'.format(
                main_object._name.replace('.', '_')),
            raise_if_not_found=False
        )
        template_key = tmpl and tmpl.key \
            or 'cms_delete_content.delete_confirm'
        return template_key

    def get_cancel_delete_url(self, main_object):
        if 'website_url' in main_object:
            return main_object.website_url
        elif request.httprequest.referrer:
            return request.httprequest.referrer
        return '/'

    def handle_delete_confirm(self, model, model_id, **kwargs):
        main_object = request.env[model].browse(model_id)
        if main_object.exists():
            template_key = self.get_template_key(main_object)
            return request.render(
                template_key, {
                    'main_object': main_object,
                    'delete_url': main_object.cms_delete_url,
                    'cancel_delete_url':
                        self.get_cancel_delete_url(main_object),
                })
        return request.not_found()

    def msg_content_deleted(self, model, main_object_values):
        model_name = request.env[model]._description
        return _('%s deleted.') % model_name

    def handle_delete(self, model, model_id, **kwargs):
        main_object = request.env[model].browse(model_id)
        if main_object.exists():
            redirect = kwargs.get('redirect', main_object.cms_after_delete_url)
            main_object_values = main_object.read()
            main_object.unlink()
            if request.website:
                request.website.add_status_message(
                    self.msg_content_deleted(model, main_object_values))
            return werkzeug.utils.redirect(redirect)
        return request.not_found()


class DeleteController(http.Controller, DeleteMixin):
    """Controller for handling model deletion."""

    @http.route(
        '/cms/<string:model>/<int:model_id>/delete/confirm',
        type='http', auth="user", website=True)
    def delete_confirm(self, model, model_id, **kwargs):
        return self.handle_delete_confirm(model, model_id, **kwargs)

    # TODO: should we use `DELETE` method?
    @http.route(
        '/cms/<string:model>/<int:model_id>/delete',
        type='http', auth="user", website=True, methods=['POST'])
    def delete(self, model, model_id, **kwargs):
        return self.handle_delete(model, model_id, **kwargs)
