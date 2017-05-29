# -*- coding: utf-8 -*-
# Copyright 2017 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import models, fields, api, exceptions, tools, _


class AutoSetupMany2one(fields.Many2one):
    """Auto set comodel_name."""

    def _setup_attrs(self, model, name):
        super(AutoSetupMany2one, self)._setup_attrs(model, name)
        self.comodel_name = model._name


class AutoSetupOne2many(fields.One2many):
    """Auto set comodel_name."""

    def _setup_attrs(self, model, name):
        super(AutoSetupOne2many, self)._setup_attrs(model, name)
        self.comodel_name = model._name


class CMSParentMixin(models.AbstractModel):
    """Base functionalities for parent/children structure."""

    _name = "cms.parent.mixin"
    _description = "A mixin for providing parent/children features"
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'

    parent_left = fields.Integer('Left Parent', select=1)
    parent_right = fields.Integer('Right Parent', select=1)
    parent_id = AutoSetupMany2one(
        string='Parent',
        comodel_name='cms.parent.mixin',
        domain=lambda self: self._domain_parent_id(),
        ondelete='cascade',
    )
    children_ids = AutoSetupOne2many(
        string='Children',
        inverse_name='parent_id',
        comodel_name='cms.parent.mixin'
    )

    @api.model
    def _domain_parent_id(self):
        return []

    @api.constrains('parent_id')
    def _check_parent_id(self):
        """Make sure we cannot have parent = self."""
        if self.parent_id and self.parent_id.id == self.id:
            raise exceptions.ValidationError(
                _('You cannot set the parent to itself. '
                  'Item: "%s"') % self.name
            )

    @api.multi
    def open_children(self):
        """Action to open tree view of children pages."""
        self.ensure_one()
        domain = [
            ('parent_id', '=', self.id),
        ]
        context = {
            'default_parent_id': self.id,
        }
        context.update(self._open_children_context())
        return {
            'name': _('Children'),
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'target': 'current',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': context,
        }

    def _open_children_context(self):
        """Override to inject custom values in context."""
        return {}

    @api.multi
    @tools.ormcache('self')
    def hierarchy(self):
        """Walk trough parent/children hierarchy and get a list of items.

        You can easily create a contextual nav (like breadcrumbs) with it.
        """
        self.ensure_one()
        if not self.parent_id:
            return ()
        current = self
        parts = []
        while current.parent_id:
            parts.insert(0, current.parent_id)
            current = current.parent_id
        return parts

    @api.multi
    @tools.ormcache('self')
    def path(self):
        """Walk trough page hierarchy to build its nested name."""
        self.ensure_one()
        if not self.parent_id:
            return '/'
        parts = [x.name for x in self.hierarchy()]
        parts.insert(0, '')
        return u'/'.join(parts)

    @api.multi
    def name_get(self):
        """Format displayed name."""
        if not self.env.context.get('include_path'):
            return super(CMSParentMixin, self).name_get()
        res = []
        for item in self:
            res.append((item.id,
                        item.path().rstrip('/') + ' > ' + item.name))
        return res

    def _get_listing_domain(self, direct=True, extra_domain=None, **kw):
        if direct:
            domain = [('parent_id', '=', self.id)]
        else:
            # Parent left/right explained
            # https://answers.launchpad.net/openobject-server/+question/186704
            # B is a descendant of A in the hierarchy (defined by parent_id) if
            # A.parent_left < B.parent_left,
            # B.parent_right and B.parent_left,
            # B.parent_right < A.parent_right
            domain = [
                ('parent_left', '>', self.parent_left),
                ('parent_right', '<', self.parent_right)
            ]
        domain.extend(extra_domain or [])
        return domain

    @api.model
    def get_listing(self, direct=True, extra_domain=None,
                    limit=None, order=None, **kw):
        """Return items down in the hierarchy.

        :param direct: to include only direct children.
        When falsy all the items down in the hierarchy will be considered
        :param extra_domain: provide your custom domain for filtering children
        :param limit: to limit search results
        """
        domain = self._get_listing_domain(
            direct=direct, extra_domain=extra_domain, **kw)
        return self.search(
            domain, limit=limit, order=order or self._parent_order)
