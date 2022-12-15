import os
from urllib.parse import quote
from config import BASE_PATH, ErrorInfo
from app import db
from app.model import VisibleDir
from tests.auth.untils import generate_visible_dir
from tests.base.test_base import BaseUnittestCase


class MultiFileActionTestCase(BaseUnittestCase):

    def setUp(self) -> None:
        super(MultiFileActionTestCase, self).setUp()

        # 生成可见目录
        generate_visible_dir()

        # 生成测试文件
        self.test_filepath_list = []
        for i in range(3):
            test_file_path = os.path.abspath(os.path.join(self.test_dir_path, '{}.txt'.format(i)))
            with open(test_file_path, 'wb') as file:
                file.write(b'')
                file.close()
            self.test_filepath_list.append(test_file_path)

        # 管理员登录
        self.login('admin', '123456')

    def tearDown(self) -> None:
        super(MultiFileActionTestCase, self).tearDown()
        for filepath in self.test_filepath_list:
            if os.path.exists(filepath):
                os.remove(filepath)

    def test_delete_fail(self):
        """删除多个文件：只要有一个失败，所有的文件都不会被删除"""
        # 构造请求数据
        data = []
        for filepath in self.test_filepath_list:
            data.append(quote(filepath))
        data.append(quote('A:/'))

        # 发送请求
        response = self.client.post(
            self.url_for('main.remove'),
            data='path=' + '&path='.join(data),
            follow_redirects=True,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )

        # 检查请求效果
        self.assertTrue(response.status_code == 404)
        for filepath in self.test_filepath_list:
            self.assertTrue(os.path.exists(filepath))

    def test_delete(self):
        """删除多个文件成功"""
        # 构造请求数据
        data = []
        for filepath in self.test_filepath_list:
            data.append(quote(filepath))

        # 发送请求
        response = self.client.post(
            self.url_for('main.remove'),
            data='path=' + '&path='.join(data),
            follow_redirects=True,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )

        # 检查请求效果
        self.assertTrue(response.status_code == 200)
        for filepath in self.test_filepath_list:
            self.assertFalse(os.path.exists(filepath))

    def test_move_fail(self):
        """移动多个文件：只要有一个失败，所有的文件都不会被移动"""
        # 构造请求数据
        data = []
        for filepath in self.test_filepath_list:
            data.append(quote(filepath))
        data.append(quote('A:/'))

        # 发送请求
        target_file_path = os.path.realpath(os.path.join(BASE_PATH, 'admin_dir'))
        response = self.client.post(
            self.url_for('main.move'),
            data='target-file-path={}&source-file-path={}'.format(
                quote(target_file_path),
                '&source-file-path='.join(data)
            ),
            follow_redirects=True,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )

        # 检查请求效果
        self.assertTrue(response.status_code == 404)
        for filepath in self.test_filepath_list:
            self.assertTrue(os.path.exists(filepath))

    def test_move(self):
        """移动多个文件成功"""
        # 构造请求数据
        data = []
        for filepath in self.test_filepath_list:
            data.append(quote(filepath))

        # 发送请求
        target_file_path = os.path.realpath(os.path.join(BASE_PATH, 'admin_dir'))
        response = self.client.post(
            self.url_for('main.move'),
            data='target-file-path={}&source-file-path={}'.format(
                quote(target_file_path),
                '&source-file-path='.join(data)
            ),
            follow_redirects=True,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )

        # 检查请求效果
        self.assertTrue(response.status_code == 200)
        for filepath in self.test_filepath_list:
            self.assertFalse(os.path.exists(filepath))
            new_filepath = os.path.join(target_file_path, os.path.basename(filepath))
            self.assertTrue(os.path.exists(new_filepath))
            os.remove(new_filepath)

    def test_copy_fail(self):
        """复制多个文件：只要有一个失败，所有的文件都不会被复制"""
        # 构造请求数据
        data = []
        for filepath in self.test_filepath_list:
            data.append(quote(filepath))
        data.append(quote('A:/'))

        # 发送请求
        target_file_path = os.path.realpath(os.path.join(BASE_PATH, 'admin_dir'))
        response = self.client.post(
            self.url_for('main.copy_file'),
            data='target-file-path={}&source-file-path={}'.format(
                quote(target_file_path),
                '&source-file-path='.join(data)
            ),
            follow_redirects=True,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )

        # 检查请求结果
        self.assertTrue(response.status_code == 404)
        exists = False
        for filepath in self.test_filepath_list:
            new_filepath = os.path.abspath(os.path.join(target_file_path, os.path.basename(filepath)))
            exists = os.path.exists(new_filepath)
            if exists:
                os.remove(new_filepath)
        self.assertFalse(exists)

    def test_copy(self):
        """复制多个文件成功"""
        # 构造请求数据
        data = []
        for filepath in self.test_filepath_list:
            data.append(quote(filepath))

        # 发送请求
        target_file_path = os.path.realpath(os.path.join(BASE_PATH, 'admin_dir'))
        response = self.client.post(
            self.url_for('main.move'),
            data='target-file-path={}&source-file-path={}'.format(
                quote(target_file_path),
                '&source-file-path='.join(data)
            ),
            follow_redirects=True,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )

        # 检查响应
        self.assertTrue(response.status)
        all_exists = True
        for filepath in self.test_filepath_list:
            new_filepath = os.path.abspath(os.path.join(target_file_path, os.path.basename(filepath)))
            all_exists = os.path.exists(new_filepath)
            if all_exists:
                os.remove(new_filepath)
        self.assertTrue(all_exists)

    def test_multi_size_no_path(self):
        """查看多个文件大小：未选择任何路径"""
        response = self.client.get(
            self.url_for('main.dir_size'),
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json.get('status') == 0)
        self.assertTrue(response.json.get('message', '') == ErrorInfo.DIR_SIZE_NO_PATH)

    def test_multi_size_path_not_exists(self):
        """查看多个文件大小：路径不合法"""
        data = map(lambda fp: quote(fp), self.test_filepath_list)
        response = self.client.get(
            self.url_for('main.dir_size') + '?path=' + '&path='.join(data) + '&path=A:\\',
            follow_redirects=True,
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json.get('status') == 0)
        self.assertTrue(response.json.get('message') == ErrorInfo.DIR_SIZE_ILLEGAL)

    def test_multi_size_path_mount(self):
        """查看多个文件大小：路径是根目录"""
        # 添加根目录到可见目录列表
        db.session.add(VisibleDir(
            dir_path=os.path.realpath('C:\\'),
            permission='admin'
        ))
        db.session.commit()

        # 请求
        data = map(lambda fp: quote(fp), self.test_filepath_list)
        response = self.client.get(
            self.url_for('main.dir_size') + '?path=' + '&path='.join(data) + '&path=C:\\',
            follow_redirects=True,
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json.get('status') == 0)
        self.assertTrue(response.json.get('message') == ErrorInfo.DIR_SIZE_MOUNT)

    def test_multi_size(self):
        """查看多个文件大小：成功"""
        data = map(lambda fp: quote(fp), self.test_filepath_list)
        response = self.client.get(
            self.url_for('main.dir_size') + '?path=' + '&path='.join(data),
            follow_redirects=True,
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json.get('status', 0) == 1)
        self.assertTrue('result' in response.json)
        self.assertTrue('total' in response.json['result'])
        self.assertTrue('size_list' in response.json['result'])
        self.assertTrue(len(response.json['result'].get('size_list')) == len(self.test_filepath_list))
