import os
import unittest
import sqlite3
from werkzeug.test import TestResponse
from flask import current_app, url_for
from config import TestingConfig
from app import create_app, db
from app.model import Users


class BaseUnittestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(True)

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        os.remove(TestingConfig.DATABASE_PATH)

    def url_for(self, endpoint: str, *args, **kwargs) -> str:
        with self.app.test_request_context():
            result = url_for(endpoint, *args, **kwargs)
        return result

    def verify_redirect(self, response: TestResponse, location: str) -> None:
        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(response.history) == 1)
        self.assertTrue(response.history[0].status_code == 302)
        self.assertTrue(response.history[0].location == location)

    def login(self, user_name: str, user_password: str) -> Users:
        response = self.client.post(
            self.url_for('auth.login'),
            data={
                'user-name': user_name,
                'user-password': user_password,
                'current-url': self.url_for('main.index')
            },
            follow_redirects=True
        )
        self.verify_redirect(response, self.url_for('main.index'))
        user: Users = Users.query.filter_by(user_name=user_name).first()
        self.assertTrue(user.is_authenticated)

        return user

    def logout(self) -> None:
        response = self.client.post(self.url_for('auth.logout'), follow_redirects=True)
        self.verify_redirect(response, self.url_for('main.index'))


class BaseTestCase(BaseUnittestCase):

    def setUp(self) -> None:
        super(BaseTestCase, self).setUp()
        self.con = sqlite3.connect(TestingConfig.DATABASE_PATH)
        self.cursor = self.con.cursor()

    def tearDown(self) -> None:
        self.cursor.close()
        self.con.close()
        super(BaseTestCase, self).tearDown()

    def test_app_exists(self):
        """检查应用是否启动成功"""
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        """检查应用是否处于测试状态"""
        self.assertTrue(current_app.config['TESTING'])

    def test_db_exists(self):
        """检查数据库文件是否会生成"""
        self.assertTrue(os.path.exists(TestingConfig.DATABASE_PATH))

    def test_user_table_exists(self):
        """检查数据库的users表是否会自动生成"""
        result = self.cursor.execute(
            'SELECT COUNT(*) FROM `sqlite_master` WHERE `type`="table" AND `name`="users";'
        ).fetchone()
        self.assertTrue(result[0] == 1)

    def test_admin_exists(self):
        """自动插入管理员记录"""
        result = self.cursor.execute('SELECT count(*) FROM `users` WHERE user_name="admin";').fetchone()
        self.assertTrue(result[0] == 1)

    def test_405_to_404(self):
        """405响应404"""
        response = self.client.get(self.url_for('auth.logout'), follow_redirects=True)
        self.assertTrue(response.status_code == 404)

    def test_403_to_404(self):
        """403响应404"""
        # TODO 待测试
        # response = self.client.get(self.url_for('auth.logout'), follow_redirects=True)
        # self.assertTrue(response.status_code == 404)
        pass

    def test_visible_dir_table_exists(self):
        """检查数据库的visible_dir表是否会自动生成"""
        result = self.cursor.execute(
            'SELECT COUNT(*) FROM `sqlite_master` WHERE `type`="table" AND `name`="visible_dir"'
        ).fetchone()
        self.assertTrue(result[0] == 1)
