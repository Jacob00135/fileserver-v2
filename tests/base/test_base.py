import os
import unittest
from flask import current_app
from config import TestingConfig
from app import create_app, db


class BaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        os.remove(TestingConfig.DATABASE_PATH)

    def test_app_exists(self):
        """检查应用是否启动成功"""
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        """检查应用是否处于测试状态"""
        self.assertTrue(current_app.config['TESTING'])

    def test_db_exists(self):
        """检查数据库文件是否会生成"""
        self.assertTrue(os.path.exists(TestingConfig.DATABASE_PATH))

