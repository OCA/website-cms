# Copyright 2017-2018 Camptocamp - Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


import json

import werkzeug

from odoo import _, http
from odoo.http import request


class DeleteMixin(object):

    delete_confirm_template = "cms_delete_content.delete_confirm"

    def get_main_object(self, model, model_id):
        main_object = request.env[model].browse(model_id)
        if main_object.exists():
            return main_object
        raise werkzeug.exceptions.NotFound(_("model: %s id: %s") % (model, model_id))

    def handle_delete_confirm(self, model, model_id, **kwargs):
        """Render modal for delete confirmation. Called via JS.

        :param model: odoo model name
        :param model_id: odoo model id
        :param kwargs: extra request args, ``redirect`` only used ATM
        :return: rendered modal template
        """
        main_object = self.get_main_object(model, model_id)
        return request.env.ref(self.delete_confirm_template).render(
            {
                "main_object": main_object,
                "delete_url": main_object.cms_delete_url,
                "redirect": kwargs.get("redirect", main_object.cms_after_delete_url),
            }
        )

    def handle_delete(self, model, model_id, **kwargs):
        """Delete a content. Called via JS.

        :param model: odoo model name
        :param model_id: odoo model id
        :param kwargs: extra request args, ``redirect`` only used ATM
        :return: json data to handle redirect and status message
        """
        main_object = self.get_main_object(model, model_id)
        result = {
            "redirect": kwargs.get("redirect", " ").strip(),
            "message": "",
        }
        msg = main_object.msg_content_deleted()
        main_object.unlink()
        if result["redirect"]:
            # put message in session if redirecting
            request.env["website"].add_status_message(msg)
        else:
            # otherwise return it and handle it via JS
            result["message"] = msg
        return json.dumps(result)


class DeleteController(http.Controller, DeleteMixin):
    """Controller for handling model deletion."""

    @http.route(
        "/cms/delete/<string:model>/<int:model_id>/confirm",
        type="http",
        auth="user",
        website=True,
    )
    def delete_confirm(self, model, model_id, **kwargs):
        return self.handle_delete_confirm(model, model_id, **kwargs)

    # TODO: should we use `DELETE` method?
    @http.route(
        "/cms/delete/<string:model>/<int:model_id>",
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def delete(self, model, model_id, **kwargs):
        return self.handle_delete(model, model_id, **kwargs)
