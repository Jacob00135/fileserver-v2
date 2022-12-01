import os
from urllib.parse import quote
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
            data='&path='.join(data),
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
            data='&path=' + '&path='.join(data),
            follow_redirects=True,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )

        # 检查请求效果
        self.assertTrue(response.status_code == 200)
        for filepath in self.test_filepath_list:
            self.assertFalse(os.path.exists(filepath))
