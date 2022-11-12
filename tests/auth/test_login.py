from tests.base.test_base import BaseUnittestCase


class LoginTestCase(BaseUnittestCase):

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
