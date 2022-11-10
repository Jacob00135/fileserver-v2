import unittest
from flask import current_app
from app import create_app


class BaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self) -> None:
        self.app_context.pop()

    def test_app_exists(self):
        """检查应用是否启动成功"""
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        """检查应用是否处于测试状态"""
        self.assertTrue(current_app.config['TESTING'])

