import os
from config import BASE_PATH
from app import db
from app.model import Users
from tests.auth.untils import generate_visible_dir
from tests.base.test_base import BaseUnittestCase


class FileActionTestCase(BaseUnittestCase):

    def setUp(self) -> None:
        super(FileActionTestCase, self).setUp()

        # 生成可见目录
        generate_visible_dir()

        # 生成测试文件
        self.test_file_path = os.path.realpath(os.path.join(BASE_PATH, 'test_file.txt'))
        with open(self.test_file_path, 'wb') as file:
            file.write(b'')
            file.close()

        # 创建测试用户
        self.user = Users(user_name='jacob1', user_password='123456')
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self) -> None:
        super(FileActionTestCase, self).tearDown()
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    def test_download_file_forbidden(self):
        """下载文件：权限不够"""
        response = self.client.get(
            self.url_for('main.download', path=self.test_file_path),
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 404)
        self.login(self.user.user_name, '123456')
        response = self.client.get(
            self.url_for('main.download', path=self.test_file_path),
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 404)

    def test_download_file(self):
        """下载文件成功"""
        self.login('admin', '123456')
        response = self.client.get(
            self.url_for('main.download', path=self.test_file_path),
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)

    def test_remove_file_forbidden(self):
        """删除文件失败：权限不够"""
        response = self.client.post(
            self.url_for('main.remove'),
            data={'path': self.test_file_path},
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 404)
        self.login(self.user.user_name, '123456')
        response = self.client.post(
            self.url_for('main.remove'),
            data={'path': self.test_file_path},
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 404)

    def test_remove_file(self):
        """删除文件成功"""
        self.login('admin', '123456')
        response = self.client.post(
            self.url_for('main.remove'),
            data={'path': self.test_file_path},
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertFalse(os.path.exists(self.test_file_path))

    def test_rename_file_forbidden(self):
        """重命名文件失败：权限不够"""
        response = self.client.post(
            self.url_for('main.rename'),
            data={'path': self.test_file_path, 'new-file-name': 'test.txt'},
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 404)
        self.login(self.user.user_name, '123456')
        response = self.client.post(
            self.url_for('main.rename'),
            data={'path': self.test_file_path, 'new-file-name': 'test.txt'},
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 404)

    def test_rename_filename_illegal(self):
        """重命名文件失败：名称包含不合法字符"""
        self.login('admin', '123456')
        new_filename = 'test\\.txt'
        response = self.client.post(
            self.url_for('main.rename'),
            data={'path': self.test_file_path, 'new-file-name': new_filename},
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(os.path.exists(self.test_file_path))
        self.assertFalse(os.path.exists(new_filename))

    def test_rename_file_exists(self):
        """重命名文件失败：同目录下已有相同名字的文件"""
        self.login('admin', '123456')
        response = self.client.post(
            self.url_for('main.rename'),
            data={'path': self.test_file_path, 'new-file-name': 'requirements.txt'},
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(os.path.exists(self.test_file_path))

    def test_test_rename_file(self):
        """重命名文件成功"""
        self.login('admin', '123456')
        new_filename = 'test.txt'
        response = self.client.post(
            self.url_for('main.rename'),
            data={'path': self.test_file_path, 'new-file-name': new_filename},
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertFalse(os.path.exists(self.test_file_path))
        new_path = os.path.realpath(os.path.join(os.path.dirname(self.test_file_path), new_filename))
        self.assertTrue(os.path.exists(new_path))
        os.remove(new_path)
