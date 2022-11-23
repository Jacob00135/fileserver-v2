import os
import shutil
from config import BASE_PATH
from app import db
from app.model import Users, VisibleDir
from tests.auth.untils import generate_visible_dir
from tests.base.test_base import BaseUnittestCase


class DirActionTestCase(BaseUnittestCase):

    def setUp(self) -> None:
        super(DirActionTestCase, self).setUp()

        # 生成可见目录
        generate_visible_dir()

        # 生成测试目录
        self.test_dirname = 'test_dir'
        self.test_sub_dirname = 'sub_dir'
        self.test_filename_1 = 'test1.txt'
        self.test_filename_2 = 'test2.txt'
        self.test_dir_path = os.path.abspath(os.path.join(BASE_PATH, self.test_dirname))
        self.test_sub_dir_path = os.path.abspath(os.path.join(self.test_dir_path, self.test_sub_dirname))
        self.test_filename_path_1 = os.path.abspath(os.path.join(self.test_dir_path, self.test_filename_1))
        self.test_filename_path_2 = os.path.abspath(os.path.join(self.test_sub_dir_path, self.test_filename_2))
        os.mkdir(self.test_dir_path)
        os.mkdir(self.test_sub_dir_path)
        with open(self.test_filename_path_1, 'wb') as file:
            file.write(b'')
            file.close()
        with open(self.test_filename_path_2, 'wb') as file:
            file.write(b'')
            file.close()

        # 创建测试用户
        self.user = Users(user_name='jacob1', user_password='123456')
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self) -> None:
        super(DirActionTestCase, self).tearDown()
        if os.path.exists(self.test_dir_path):
            shutil.rmtree(self.test_dir_path)

    def test_remove_visible_dir(self):
        """删除目录失败：尝试删除可见目录"""
        db.session.add(VisibleDir(
            dir_path=self.test_dir_path,
            permission='anonymous_user'
        ))
        db.session.commit()
        self.login('admin', '123456')
        response = self.client.post(
            self.url_for('main.remove'),
            data={'path': self.test_dir_path},
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(os.path.exists(self.test_dir_path))

    def test_remove_dir(self):
        """删除目录成功"""
        self.login('admin', '123456')
        response = self.client.post(
            self.url_for('main.remove'),
            data={'path': self.test_dir_path},
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertFalse(os.path.exists(self.test_dir_path))

    def test_rename_visible_dir(self):
        """重命名目录失败：尝试重命名可见目录"""
        db.session.add(VisibleDir(
            dir_path=self.test_dir_path,
            permission='anonymous_user'
        ))
        db.session.commit()
        self.login('admin', '123456')
        new_filename = 'test_dir_1'
        new_file_path = os.path.abspath(os.path.join(BASE_PATH, new_filename))
        response = self.client.post(
            self.url_for('main.rename'),
            data={
                'path': self.test_dir_path,
                'new-file-name': new_filename
            },
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(os.path.exists(self.test_dir_path))
        self.assertFalse(os.path.exists(new_file_path))

    def test_rename_dir(self):
        """重命名目录成功"""
        self.login('admin', '123456')
        new_filename = 'test_dir_1'
        new_file_path = os.path.abspath(os.path.join(BASE_PATH, new_filename))
        response = self.client.post(
            self.url_for('main.rename'),
            data={
                'path': self.test_dir_path,
                'new-file-name': new_filename
            },
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertFalse(os.path.exists(self.test_dir_path))
        self.assertTrue(os.path.exists(new_file_path))
        shutil.rmtree(new_file_path)

    def test_move_visible_dir(self):
        """移动目录失败：尝试移动可见目录"""
        db.session.add(VisibleDir(
            dir_path=self.test_dir_path,
            permission='anonymous_user'
        ))
        db.session.commit()
        self.login('admin', '123456')
        target_dir_path = os.path.realpath(os.path.join(BASE_PATH, 'admin_dir'))
        target_path = os.path.abspath(os.path.join(target_dir_path, self.test_dirname))
        response = self.client.post(
            self.url_for('main.move'),
            data={
                'source-file-path': self.test_dir_path,
                'target-file-path': target_dir_path
            },
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(os.path.exists(self.test_dir_path))
        self.assertFalse(os.path.exists(target_path))

    def test_move_dir(self):
        """移动目录成功"""
        self.login('admin', '123456')
        target_dir_path = os.path.realpath(os.path.join(BASE_PATH, 'admin_dir'))
        target_path = os.path.abspath(os.path.join(target_dir_path, self.test_dirname))
        response = self.client.post(
            self.url_for('main.move'),
            data={
                'source-file-path': self.test_dir_path,
                'target-file-path': target_dir_path
            },
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertFalse(os.path.exists(self.test_dir_path))
        self.assertTrue(os.path.exists(target_path))
        shutil.rmtree(target_path)

    def test_copy_dir(self):
        """复制目录成功"""
        self.login('admin', '123456')
        target_dir_path = os.path.realpath(os.path.join(BASE_PATH, 'admin_dir'))
        target_path = os.path.abspath(os.path.join(target_dir_path, self.test_dirname))
        response = self.client.post(
            self.url_for('main.copy_file'),
            data={
                'source-file-path': self.test_dir_path,
                'target-file-path': target_dir_path
            },
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(os.path.exists(self.test_dir_path))
        self.assertTrue(os.path.exists(target_path))
        shutil.rmtree(target_path)
