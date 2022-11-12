from app import db
from app.model import Users
from tests.base.test_base import BaseUnittestCase


class UsersModelTestCase(BaseUnittestCase):

    def test_user_password_attribute(self):
        """禁止访问Users对象的user_password属性"""
        admin: Users = Users.query.filter_by(user_name='admin').first()
        with self.assertRaises(AttributeError):
            print(admin.user_password)

    def test_user_password_hash(self):
        """对赋值Users对象的user_password赋值，会自动计算user_password_hash"""
        admin: Users = Users.query.filter_by(user_name='admin').first()
        before_password_hash = admin.user_password_hash
        admin.user_password = '654321'
        self.assertTrue(admin.user_password_hash != before_password_hash)

    def test_verify_password(self):
        """Users对象的验证密码相等的verify_password方法"""
        admin: Users = Users.query.filter_by(user_name='admin').first()
        admin.user_password = '654321'
        self.assertTrue(admin.verify_password('654321'))
        self.assertFalse(admin.verify_password('123456'))

    def test_is_admin(self):
        """Users对象的判断是否是管理员的is_admin方法"""
        # 获取管理员对象
        admin: Users = Users.query.filter_by(user_name='admin').first()

        # 添加一个不是管理员的用户
        user = Users(user_name='Jacob', user_password='098765')
        db.session.add(user)
        db.session.commit()

        self.assertTrue(admin.is_admin())
        self.assertFalse(user.is_admin())
