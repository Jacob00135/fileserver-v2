import os
from app import db
from config import BASE_PATH
from app.model import Users, AnonymousUser, VisibleDir
from tests.base.test_base import BaseUnittestCase


class VisibleDirModelTestCase(BaseUnittestCase):

    def setUp(self) -> None:
        super(VisibleDirModelTestCase, self).setUp()
        self.dir_1 = VisibleDir(
            dir_path=os.path.join(BASE_PATH, 'app/templates'),
            permission='anonymous_user'
        )
        self.dir_2 = VisibleDir(
            dir_path=os.path.join(BASE_PATH, 'app/static'),
            permission='user'
        )
        self.dir_3 = VisibleDir(
            dir_path=BASE_PATH,
            permission='admin'
        )
        db.session.add_all([self.dir_1, self.dir_2, self.dir_3])
        db.session.commit()

    def test_permission_enum(self):
        """VisibleDir对象初始化时权限值约束"""
        dir_path = os.path.join(BASE_PATH, 'admin_dir')
        with self.assertRaises(ValueError):
            VisibleDir(
                dir_path=dir_path,
                permission='root'
            )
        self.assertTrue(VisibleDir.query.filter_by(dir_path=dir_path).first() is None)

    def test_anonymous_user_permission(self):
        """VisibleDir对象的can方法：游客权限"""
        anonymous_user = AnonymousUser()
        self.assertTrue(self.dir_1.can(anonymous_user))
        self.assertFalse(self.dir_2.can(anonymous_user))
        self.assertFalse(self.dir_3.can(anonymous_user))

    def test_user_permission(self):
        """VisibleDir对象的can方法：普通用户权限"""
        user = Users(user_name='Jacob', user_password='123456')
        db.session.add(user)
        db.session.commit()
        self.assertTrue(self.dir_1.can(user))
        self.assertTrue(self.dir_2.can(user))
        self.assertFalse(self.dir_3.can(user))

    def test_admin_permission(self):
        """VisibleDir对象的can方法：管理员权限"""
        admin = Users.query.filter_by(user_name='admin').first()
        self.assertTrue(self.dir_1.can(admin))
        self.assertTrue(self.dir_2.can(admin))
        self.assertTrue(self.dir_3.can(admin))
