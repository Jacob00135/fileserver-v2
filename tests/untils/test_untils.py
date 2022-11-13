from tests.base.test_base import BaseUnittestCase
from config import ErrorInfo
from app.untils import check_legal


class UntilsTestCase(BaseUnittestCase):

    def test_check_legal_param_error(self):
        """check_legal函数检查：传入参数不合法"""
        with self.assertRaises(ValueError):
            check_legal('123456', 'user_token')

    def test_user_name_null(self):
        """用户名检查：为空"""
        check_result = check_legal('', 'user_name')
        self.assertFalse(check_result['legal'])
        self.assertTrue(check_result['error_info'] == ErrorInfo.USER_NAME_NULL)

    def test_user_name_length(self):
        """用户名检查：长度不合法"""
        check_result = check_legal('0123456789abcdefghijklmnopqrstuvwxyz', 'user_name')
        self.assertFalse(check_result['legal'])
        self.assertTrue(check_result['error_info'] == ErrorInfo.USER_NAME_ILLEGAL)

    def test_user_name_illegal(self):
        """用户名检查：包含不合法字符"""
        check_result = check_legal('$%0123456789', 'user_name')
        self.assertFalse(check_result['legal'])
        self.assertTrue(check_result['error_info'] == ErrorInfo.USER_NAME_ILLEGAL)

    def test_user_name_legal(self):
        """用户名检查：合法"""
        check_result = check_legal('server_admin', 'user_name')
        self.assertTrue(check_result['legal'])
        self.assertTrue(check_result['error_info'] == '')

    def test_user_password_null(self):
        """用户密码检查：为空"""
        check_result = check_legal('', 'user_password')
        self.assertFalse(check_result['legal'])
        self.assertTrue(check_result['error_info'] == ErrorInfo.USER_PASSWORD_NULL)

    def test_user_password_length(self):
        """用户密码检查：长度不合法"""
        check_result = check_legal('0123456789abcdefghijklmnopqrstuvwxyz', 'user_password')
        self.assertFalse(check_result['legal'])
        self.assertTrue(check_result['error_info'] == ErrorInfo.USER_PASSWORD_ILLEGAL)

    def test_user_password_illegal(self):
        """用户密码检查：包含不合法字符"""
        check_result = check_legal('$%0123456789', 'user_password')
        self.assertFalse(check_result['legal'])
        self.assertTrue(check_result['error_info'] == ErrorInfo.USER_PASSWORD_ILLEGAL)

    def test_user_password_legal(self):
        """用户密码检查：合法"""
        check_result = check_legal('197011timestamp', 'user_password')
        self.assertTrue(check_result['legal'])
        self.assertTrue(check_result['error_info'] == '')
