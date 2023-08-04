# Copyright 2018 Simone Orsi (Camptocamp)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import api, exceptions, fields, models


class CMSInfoMixin(models.AbstractModel):
    """Provide core information for CMS records."""

    _name = "cms.info.mixin"
    _description = "CMS Info mixin"

    def _cms_make_url(self, action):
        return "/cms/{}/{}".format(action, self._name)

    @property
    def cms_create_url(self):
        return self._cms_make_url("create")

    @property
    def cms_search_url(self):
        return self._cms_make_url("search")

    @property
    def cms_edit_url_base(self):
        return self._cms_make_url("edit")

    @property
    def cms_delete_url_base(self):
        return self._cms_make_url("delete")

    @property
    def cms_after_delete_url(self):
        return "/"

    url = fields.Char(
        string="URL",
        compute="_compute_cms_url",
        compute_sudo=True,
    )
    cms_edit_url = fields.Char(
        string="CMS edit URL",
        compute="_compute_cms_url",
        compute_sudo=True,
    )
    cms_delete_url = fields.Char(
        string="CMS delete URL",
        compute="_compute_cms_url",
        compute_sudo=True,
    )
    cms_delete_confirm_url = fields.Char(
        string="CMS delete confirm URL",
        compute="_compute_cms_url",
        compute_sudo=True,
    )
    cms_copy_url = fields.Char(
        string="CMS copy URL",
        compute="_compute_cms_url",
        compute_sudo=True,
    )

    def _compute_cms_url(self):
        for rec in self:
            rec.url = rec._get_cms_url()
            rec.cms_edit_url = rec._get_cms_edit_url()
            rec.cms_copy_url = rec._get_cms_copy_url()
            rec.update(rec._get_cms_delete_urls())

    def _get_cms_url(self):
        # TODO: add glue module for website
        # TODO: should be empty by default?
        base_view_url = self._cms_make_url("view")
        return f"{base_view_url}/{self.id}"

    def _get_cms_edit_url(self):
        base_edit_url = self.cms_edit_url_base
        return f"{base_edit_url}/{self.id}"

    def _get_cms_copy_url(self):
        base_url = self._cms_make_url("copy")
        return f"{base_url}/{self.id}"

    def _get_cms_delete_urls(self):
        base_url = self.cms_delete_url_base
        return {
            "cms_delete_url": "{}/{}".format(base_url, self.id),
            "cms_delete_confirm_url": "{}/{}/confirm".format(base_url, self.id),
        }

    def cms_is_owner(self, uid=None):
        self.ensure_one()
        uid = uid or self.env.user.id
        return self.create_uid.id == uid

    @api.model
    def cms_can_create(self):
        return self.check_access_rights("create", raise_exception=False)

    def _cms_check_perm(self, mode):
        self.ensure_one()
        try:
            self.check_access_rights(mode)
            self.check_access_rule(mode)
            can = True
        except exceptions.AccessError:
            can = False
        return can

    def cms_can_edit(self):
        return self._cms_check_perm("write")

    def cms_can_delete(self):
        return self._cms_check_perm("unlink")

    def cms_can_publish(self):
        # TODO: improve this
        return self.cms_can_edit()

    def cms_info(self):
        # do not use `ensure_one` so we can use this on an empty recordset
        info = {}.fromkeys(
            (
                "is_owner",
                "can_edit",
                "can_create",
                "can_publish",
                "can_delete",
                "create_url",
                "edit_url",
                "delete_url",
            ),
            None,
        )
        if self:
            # we have a record indeed
            info.update(
                {
                    # make sure it works even on empty recordsets
                    "is_owner": self.cms_is_owner() if self else None,
                    "can_edit": self.cms_can_edit(),
                    "can_publish": self.cms_can_publish(),
                    "can_delete": self.cms_can_delete(),
                    "edit_url": self.cms_edit_url,
                    "delete_url": self.cms_delete_confirm_url,
                }
            )
        info.update(
            {
                # class-level info
                "create_url": self.cms_create_url,
                "can_create": self.cms_can_create(),
            }
        )
        return info
