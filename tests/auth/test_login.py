from werkzeug.test import TestResponse
from tests.base.test_base import BaseUnittestCase


class LoginTestCase(BaseUnittestCase):

    def request_update_password(self, new_password: str) -> TestResponse:
        response = self.client.post(
            self.url_for('auth.update_password'),
            data={
                'current-url': self.url_for('main.index'),
                'new-password': new_password,
            },
            follow_redirects=True
        )
        return response

    def test_login(self):
        """登录成功"""
        self.login('admin', '123456')

    def test_repeat_login(self):
        """登录失败：重复登录"""
        self.login('admin', '123456')

        response = self.client.post(
            self.url_for('auth.login'),
            data={
                'user-name': 'admin',
                'user-password': '123456',
                'current-url': self.url_for('main.index')
            },
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)

    def test_logout(self):
        """登出"""
        self.login('admin', '123456')
        self.logout()

    def test_update_password_anonymous(self):
        """修改密码失败：未登录"""
        response = self.request_update_password('123456')
        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(response.history) == 2)
        self.assertTrue(response.history[-1].location == self.url_for('main.index'))

    def test_update_password_illegal(self):
        """修改密码成功"""
        admin = self.login('admin', '123456')
        response = self.request_update_password('654321')
        self.verify_redirect(response, self.url_for('main.index'))
        self.assertTrue(admin.verify_password('654321'))
