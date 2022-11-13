from tests.base.test_base import BaseUnittestCase
from config import ErrorInfo
from app.model import Users
from app.untils import check_legal, update_user_password


class CheckLegalFuncTestCase(BaseUnittestCase):

    def test_check_type_param(self):
        """check_legal函数：传入check_type参数不合法"""
        with self.assertRaises(ValueError):
            check_legal('123456', 'user_token')

    def test_user_name_null(self):
        """check_legal函数：用户名为空"""
        check_result = check_legal('', 'user_name')
        self.assertFalse(check_result['legal'])
        self.assertTrue(check_result['error_info'] == ErrorInfo.USER_NAME_NULL)

    def test_user_name_length(self):
        """check_legal函数：用户名长度不合法"""
        check_result = check_legal('0123456789abcdefghijklmnopqrstuvwxyz', 'user_name')
        self.assertFalse(check_result['legal'])
        self.assertTrue(check_result['error_info'] == ErrorInfo.USER_NAME_ILLEGAL)

    def test_user_name_illegal(self):
        """check_legal函数：用户名包含不合法字符"""
        check_result = check_legal('$%0123456789', 'user_name')
        self.assertFalse(check_result['legal'])
        self.assertTrue(check_result['error_info'] == ErrorInfo.USER_NAME_ILLEGAL)

    def test_user_name_legal(self):
        """check_legal函数：用户名合法"""
        check_result = check_legal('server_admin', 'user_name')
        self.assertTrue(check_result['legal'])
        self.assertTrue(check_result['error_info'] == '')

    def test_user_password_null(self):
        """check_legal函数：用户密码为空"""
        check_result = check_legal('', 'user_password')
        self.assertFalse(check_result['legal'])
        self.assertTrue(check_result['error_info'] == ErrorInfo.USER_PASSWORD_NULL)

    def test_user_password_length(self):
        """check_legal函数：用户密码长度不合法"""
        check_result = check_legal('0123456789abcdefghijklmnopqrstuvwxyz', 'user_password')
        self.assertFalse(check_result['legal'])
        self.assertTrue(check_result['error_info'] == ErrorInfo.USER_PASSWORD_ILLEGAL)

    def test_user_password_illegal(self):
        """check_legal函数：用户密码包含不合法字符"""
        check_result = check_legal('$%0123456789', 'user_password')
        self.assertFalse(check_result['legal'])
        self.assertTrue(check_result['error_info'] == ErrorInfo.USER_PASSWORD_ILLEGAL)

    def test_user_password_legal(self):
        """check_legal函数：用户密码合法"""
        check_result = check_legal('197011timestamp', 'user_password')
        self.assertTrue(check_result['legal'])
        self.assertTrue(check_result['error_info'] == '')


class UpdateUserPasswordTestCase(BaseUnittestCase):

    def test_password_illegal(self):
        """update_user_password函数：用户密码不合法"""
        admin: Users = Users.query.filter_by(user_name='admin').first()
        update_result = update_user_password(admin, '[!123456]')
        self.assertFalse(update_result['success'])
        self.assertTrue(update_result['error_info'] == ErrorInfo.USER_PASSWORD_ILLEGAL)

    def test_password_same(self):
        """update_user_password函数：与原密码相同"""
        admin: Users = Users.query.filter_by(user_name='admin').first()
        update_result = update_user_password(admin, '123456')
        self.assertFalse(update_result['success'])
        self.assertTrue(update_result['error_info'] == ErrorInfo.USER_PASSWORD_SAME)

    def test_update_success(self):
        """update_user_password函数：修改成功"""
        admin: Users = Users.query.filter_by(user_name='admin').first()
        update_result = update_user_password(admin, '654321')
        self.assertTrue(update_result['success'])
        self.assertTrue(update_result['error_info'] == '')
