from app import db
from app.model import Users
from tests.base.test_base import BaseUnittestCase


class UserManageTestCase(BaseUnittestCase):

    def setUp(self) -> None:
        super(UserManageTestCase, self).setUp()
        self.user1 = Users(user_name='user11', user_password='123456')
        self.user2 = Users(user_name='user22', user_password='123456')
        db.session.add_all([self.user1, self.user2])
        db.session.commit()

    def test_anonymous_visit(self):
        """匿名用户访问用户管理页面"""
        response = self.client.get(self.url_for('auth.user_manage'), follow_redirects=True)
        self.assertTrue(response.status_code == 404)

    def test_user_visit(self):
        """普通用户访问用户管理页面"""
        self.login(self.user1.user_name, '123456')
        response = self.client.get(self.url_for('auth.user_manage'), follow_redirects=True)
        self.assertTrue(response.status_code == 404)

    def test_admin_visit(self):
        """管理员访问用户管理页面"""
        self.login('admin', '123456')
        response = self.client.get(self.url_for('auth.user_manage'), follow_redirects=True)
        self.assertTrue(response.status_code == 200)

    def test_anonymous_add_user(self):
        """用户管理：匿名用户添加用户"""
        response = self.client.post(
            self.url_for('auth.add_user'),
            data={
                'user-name': 'user33',
                'user-password': '123456'
            },
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 404)

    def test_user_add_user(self):
        """用户管理：普通用户添加用户"""
        self.login(self.user1.user_name, '123456')
        response = self.client.post(
            self.url_for('auth.add_user'),
            data={
                'user-name': 'user33',
                'user-password': '123456'
            },
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 404)

    def test_admin_add_user(self):
        """用户管理：管理员添加用户"""
        self.login('admin', '123456')
        response = self.client.post(
            self.url_for('auth.add_user'),
            data={
                'user-name': 'user33',
                'user-password': '123456'
            },
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(Users.query.filter_by(user_name='user33').first() is not None)

    def test_add_user_illegal(self):
        """用户管理：添加用户时用户名不合法"""
        self.login('admin', '123456')
        response = self.client.post(
            self.url_for('auth.add_user'),
            data={
                'user-name': '%%123456%%',
                'user-password': '123456'
            },
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(Users.query.filter_by(user_name='%%123456%%').first() is None)

    def test_add_user_password_illegal(self):
        """用户管理：添加用户时密码不合法"""
        self.login('admin', '123456')
        response = self.client.post(
            self.url_for('auth.add_user'),
            data={
                'user-name': 'user33',
                'user-password': '%%123456%%'
            },
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(Users.query.filter_by(user_name='user33').first() is None)

    def test_anonymous_delete_user(self):
        """用户管理：匿名用户删除用户"""
        response = self.client.post(
            self.url_for('auth.delete_user'),
            data='user-name={}'.format(self.user1.user_name),
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 404)

    def test_user_delete_user(self):
        """用户管理：普通用户删除用户"""
        self.login(self.user2.user_name, '123456')
        response = self.client.post(
            self.url_for('auth.delete_user'),
            data='user-name={}'.format(self.user1.user_name),
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 404)

    def test_admin_delete_user(self):
        """用户管理：管理员删除用户"""
        self.login('admin', '123456')
        response = self.client.post(
            self.url_for('auth.delete_user'),
            data='user-name={}&user-name={}'.format(self.user1.user_name, self.user2.user_name),
            follow_redirects=True,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(Users.query.filter_by(user_name='user11').first() is None)
        self.assertTrue(Users.query.filter_by(user_name='user22').first() is None)

    def test_delete_user_not_exists(self):
        """用户管理：删除用户时用户不存在"""
        self.login('admin', '123456')
        response = self.client.post(
            self.url_for('auth.delete_user'),
            data='user-name={}&user-name={}user-name=user33'.format(self.user1.user_name, self.user2.user_name),
            follow_redirects=True,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(Users.query.filter_by(user_name='user11').first() is not None)
        self.assertTrue(Users.query.filter_by(user_name='user22').first() is not None)

    def test_anonymous_update_password(self):
        """用户管理：匿名用户修改密码"""
        response = self.client.post(
            self.url_for('auth.update_user_password'),
            data={
                'user-name': self.user1.user_name,
                'new-password': '654321'
            },
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 404)

    def test_user_update_password(self):
        """用户管理：普通用户修改密码"""
        self.login(self.user1.user_name, '123456')
        response = self.client.post(
            self.url_for('auth.update_user_password'),
            data={
                'user-name': self.user1.user_name,
                'new-password': '654321'
            },
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 404)

    def test_admin_update_password(self):
        """用户管理：管理员修改密码"""
        self.login('admin', '123456')
        response = self.client.post(
            self.url_for('auth.update_user_password'),
            data={
                'user-name': self.user1.user_name,
                'new-password': '654321'
            },
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(self.user1.verify_password('654321'))

    def test_update_password_illegal(self):
        """用户密码：修改密码时密码不合法"""
        self.login('admin', '123456')
        response = self.client.post(
            self.url_for('auth.update_user_password'),
            data={
                'user-name': self.user1.user_name,
                'new-password': 'abcdefghijklmnopqrstuvwxyz'
            },
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(self.user1.verify_password('123456'))
