# Copyright 2018 Simone Orsi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import exceptions
import base64
import mock
import logging
import werkzeug
logging.getLogger('PIL.PngImagePlugin').setLevel(logging.ERROR)


class BaseSecurityTestCase(object):

    @property
    def model(self):
        """Override this your test case to return a model to test."""
        raise NotImplementedError()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user_model = cls.env['res.users'].with_context(
            no_reset_password=True,
            tracking_disable=True,
            mail_create_nosubscribe=True)
        cls.user1 = user_model.create({
            'name': 'User 1',
            'login': 'user1',
            'email': 'user1@email.com',
            # make sure to have only portal group
            'groups_id': [(6, 0, [cls.env.ref('base.group_portal').id])]
        })
        cls.user2 = user_model.create({
            'name': 'User2',
            'login': 'user2',
            'email': 'user2@email.com',
            # make sure to have only portal group
            'groups_id': [(6, 0, [cls.env.ref('base.group_portal').id])]
        })
        cls.group_public = cls.env.ref('base.group_public')
        cls.user_public = user_model.create({
            'name': 'Public User',
            'login': 'publicuser',
            'email': 'publicuser@example.com',
            'groups_id': [(6, 0, [cls.group_public.id])]}
        )


class BasePermissionTestCase(BaseSecurityTestCase):
    """Base klass to test your model basic permissions.

    You can reuse this to test all your models' access.
    Just provide a proper `model` property.

    See `test_record_security` as an example.
    """

    def test_perm_create(self):
        rec = self.model.sudo(self.user1.id).create({'name': 'Foo'})
        self.assertTrue(self.model.browse(rec.id))

    def test_perm_write(self):
        rec = self.model.sudo(self.user1.id).create({'name': 'Foo'})
        rec.name = 'Baz'
        self.assertEqual(rec.name, 'Baz')

    def test_perm_write_only_owner(self):
        rec = self.model.sudo(self.user1.id).create({'name': 'Foo'})
        with self.assertRaises(exceptions.AccessError):
            rec.sudo(self.user2.id).name = 'cannot do this!'
        rec = self.model.sudo(self.user2.id).create({'name': 'Foo 2'})
        with self.assertRaises(exceptions.AccessError):
            rec.sudo(self.user1.id).name = 'cannot do this!'
        with self.assertRaises(exceptions.AccessError):
            rec.sudo(self.user_public.id).name = 'cannot do this!'

    def test_delete(self):
        rec = self.model.sudo(self.user1.id).create({'name': 'Foo'})
        rec_id = rec.id
        rec.unlink()
        self.assertFalse(self.model.browse(rec_id).exists())

        # test delete w/ attachment field
        # Reported issue https://github.com/odoo/odoo/issues/15311
        # Overridden unlink method in security mixin.
        rec = self.model.sudo(self.user1.id).create({
            'name': 'Foo',
            'image': base64.b64encode(bytes('fake image here!', 'utf-8')),
        })
        rec_id = rec.id
        rec.unlink()
        self.assertFalse(self.model.browse(rec_id).exists())

    def test_delete_only_owner(self):
        rec = self.model.sudo(self.user1.id).create({'name': 'Foo'})
        with self.assertRaises(exceptions.AccessError):
            rec.sudo(self.user2.id).unlink()
        with self.assertRaises(exceptions.AccessError):
            rec.sudo(self.user_public.id).unlink()

    def test_published(self):
        rec = self.model.sudo(self.user1.id).create({'name': 'Foo'})
        self.assertFalse(rec.website_published)
        # admin
        self.assertTrue(rec.read())
        # owner
        self.assertTrue(rec.sudo(self.user1.id).read())
        # public user
        with self.assertRaises(exceptions.AccessError):
            rec.sudo(self.user_public.id).read()
        # another portal user
        with self.assertRaises(exceptions.AccessError):
            rec.sudo(self.user2.id).read()
        # publish it!
        rec.website_published = True
        # now public user can see it
        self.assertTrue(rec.sudo(self.user_public.id).read())
        # and other portal user too
        self.assertTrue(rec.sudo(self.user2.id).read())

    def test_perm_read_group_ids(self):
        rec = self.model.sudo(self.user1.id).create({'name': 'Foo'})
        with self.assertRaises(exceptions.AccessError):
            rec.sudo(self.user2.id).name
        # sharing group
        group = self.env['res.groups'].create({'name': 'View Team'})
        self.user2.write({'groups_id': [(4, group.id)]})
        rec.write({'read_group_ids': [(4, group.id)]})
        # now user2 can read
        self.assertTrue(rec.sudo(self.user2.id).name)
        # public user still cannot access
        with self.assertRaises(exceptions.AccessError):
            rec.sudo(self.user_public.id).name

    def test_perm_write_group_ids(self):
        rec = self.model.sudo(self.user1.id).create({'name': 'Foo'})
        with self.assertRaises(exceptions.AccessError):
            rec.sudo(self.user2.id).name = 'New name here!'
        # sharing group
        group = self.env['res.groups'].create({'name': 'Write Team'})
        self.user2.write({'groups_id': [(4, group.id)]})
        rec.write({'write_group_ids': [(4, group.id)]})
        # now user2 can write
        rec.sudo(self.user2.id).name = 'New name here!'
        self.assertEqual(rec.name, 'New name here!')
        # public user still cannot access
        with self.assertRaises(exceptions.AccessError):
            rec.sudo(self.user_public.id).name = 'not me!'


class BaseSecureConverterTestCase(BaseSecurityTestCase):
    """Base klass to test secure route converter on your model.

    You can reuse this to test all your models' access via secure converter.
    Just provide a proper `model` property.

    See `test_record_security` as an example.
    """

    @property
    def model_route(self):
        return "/foo/<model('{}'):obj>".format(self.model._name)

    def test_get_converters(self):
        conv = self.env['ir.http']._get_converters()
        self.assertEqual(conv['model'].__name__, 'SecureModelConverter')

    def _mock_request(self, mocked_request, uid):
        mocked_request.cr = self.env.cr
        mocked_request.context = self.env.context
        mocked_request.session = mock.MagicMock()
        mocked_request.session.uid = uid

    def _get_converter(self):
        conv = self.env['ir.http']._get_converters()['model']
        conv = conv(self.model_route)
        conv.model = self.model._name
        return conv

    @mock.patch('odoo.addons.cms_security.models.security.request')
    @mock.patch('odoo.addons.http_routing.models.ir_http.request')
    def test_secure_convert_owner(self, mocked_request1, mocked_request2):
        rec = self.model.sudo(self.user1.id).create({'name': 'Foo'})
        self.assertFalse(rec.website_published)
        self._mock_request(mocked_request1, self.user1.id)
        self._mock_request(mocked_request2, self.user1.id)
        conv = self._get_converter()
        self.assertEqual(rec, conv.to_python(str(rec.id)))

    @mock.patch('odoo.addons.cms_security.models.security.request')
    @mock.patch('odoo.addons.http_routing.models.ir_http.request')
    def test_secure_convert_not_owner(self, mocked_request1, mocked_request2):
        rec = self.model.sudo(self.user1.id).create({'name': 'Foo'})
        self.assertFalse(rec.website_published)
        self._mock_request(mocked_request1, self.user2.id)
        self._mock_request(mocked_request2, self.user2.id)
        conv = self._get_converter()
        with self.assertRaises(werkzeug.exceptions.NotFound):
            self.assertEqual(rec, conv.to_python(str(rec.id)))

    @mock.patch('odoo.addons.cms_security.models.security.request')
    @mock.patch('odoo.addons.http_routing.models.ir_http.request')
    def test_secure_convert_not_owner_but_published(
            self, mocked_request1, mocked_request2):
        rec = self.model.sudo(self.user1.id).create({
            'name': 'Foo',
            'website_published': True,
        })
        self.assertTrue(rec.website_published)
        self._mock_request(mocked_request1, self.user2.id)
        self._mock_request(mocked_request2, self.user2.id)
        conv = self._get_converter()
        self.assertEqual(rec, conv.to_python(str(rec.id)))

    @mock.patch('odoo.addons.cms_security.models.security.request')
    @mock.patch('odoo.addons.http_routing.models.ir_http.request')
    def test_secure_convert_public_not_published(
            self, mocked_request1, mocked_request2):
        rec = self.model.sudo(self.user1.id).create({'name': 'Foo'})
        self.assertFalse(rec.website_published)
        self._mock_request(mocked_request1, self.user_public.id)
        self._mock_request(mocked_request2, self.user_public.id)
        conv = self._get_converter()
        with self.assertRaises(werkzeug.exceptions.NotFound):
            self.assertEqual(rec, conv.to_python(str(rec.id)))

    @mock.patch('odoo.addons.cms_security.models.security.request')
    @mock.patch('odoo.addons.http_routing.models.ir_http.request')
    def test_secure_convert_public_but_published(
            self, mocked_request1, mocked_request2):
        rec = self.model.sudo(self.user1.id).create({
            'name': 'Foo',
            'website_published': True,
        })
        self.assertTrue(rec.website_published)
        self._mock_request(mocked_request1, self.user_public.id)
        self._mock_request(mocked_request2, self.user_public.id)
        conv = self._get_converter()
        self.assertEqual(rec, conv.to_python(str(rec.id)))
