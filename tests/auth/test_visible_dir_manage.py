import os
from config import BASE_PATH
from app import db
from app.model import Users, VisibleDir
from tests.base.test_base import BaseUnittestCase
from tests.auth.untils import generate_visible_dir


class VisibleDirManageTestCase(BaseUnittestCase):

    def setUp(self) -> None:
        super(VisibleDirManageTestCase, self).setUp()
        self.user = Users(user_name='Jacob1', user_password='123456')
        db.session.add(self.user)
        db.session.commit()
        generate_visible_dir()

    def test_anonymous_user_visit(self):
        """游客访问可见目录管理页面"""
        response = self.client.get(self.url_for('auth.visible_dir_manage'), follow_redirects=True)
        self.assertTrue(response.status_code == 404)

    def test_user_visit(self):
        """普通用户访问可见目录管理页面"""
        self.login(self.user.user_name, '123456')
        response = self.client.get(self.url_for('auth.visible_dir_manage'), follow_redirects=True)
        self.assertTrue(response.status_code == 404)

    def test_admin_visit(self):
        """管理员访问可见目录管理页面"""
        self.login('admin', '123456')
        response = self.client.get(self.url_for('auth.visible_dir_manage'), follow_redirects=True)
        self.assertTrue(response.status_code == 200)

    def test_add_visible_dir_permission(self):
        """添加可见目录失败：无权限"""
        response = self.client.post(
            self.url_for('auth.add_visible_dir'),
            data={
                'dir-path': BASE_PATH,
                'permission': 'admin'
            },
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 404)

        self.login(self.user.user_name, '123456')
        response = self.client.post(
            self.url_for('auth.add_visible_dir'),
            data={
                'dir_path': BASE_PATH,
                'permission': 'admin'
            },
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 404)

    def test_add_visible_dir_permission_illegal(self):
        """添加可见目录：权限值不合法"""
        self.login('admin', '123456')
        dir_path = os.path.realpath(os.path.join(BASE_PATH, 'venv'))
        response = self.client.post(
            self.url_for('auth.add_visible_dir'),
            data={
                'dir-path': dir_path,
                'permission': 'root'
            },
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(VisibleDir.query.filter_by(dir_path=dir_path).first() is None)

    def test_add_visible_dir(self):
        """添加可见目录成功"""
        self.login('admin', '123456')
        dir_path = os.path.realpath(os.path.join(BASE_PATH, 'venv'))
        response = self.client.post(
            self.url_for('auth.add_visible_dir'),
            data={
                'dir-path': dir_path,
                'permission': 'admin'
            },
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(VisibleDir.query.filter_by(dir_path=dir_path).first() is not None)

    def test_delete_visible_dir_permission(self):
        """删除可见目录失败：无权限"""
        response = self.client.post(
            self.url_for('auth.delete_visible_dir'),
            data='dir-path={}'.format(BASE_PATH),
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 404)

        self.login(self.user.user_name, '123456')
        response = self.client.post(
            self.url_for('auth.delete_visible_dir'),
            data='dir-path={}'.format(BASE_PATH),
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 404)

    def test_delete_visible_dir_not_exists(self):
        """删除可见目录失败：路径不存在于数据库中"""
        self.login('admin', '123456')
        response = self.client.post(
            self.url_for('auth.delete_visible_dir'),
            data='dir-path={}&dir-path={}'.format(BASE_PATH, 'C:\\'),
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(VisibleDir.query.filter_by(dir_path=BASE_PATH).first() is not None)

    def test_delete_visible_dir(self):
        """删除可见目录成功"""
        self.login('admin', '123456')
        delete_path_list = [
            BASE_PATH,
            os.path.realpath(os.path.join(BASE_PATH, 'admin_dir')),
            os.path.realpath(os.path.join(BASE_PATH, 'app'))
        ]
        for dir_path in delete_path_list:
            self.assertTrue(VisibleDir.query.filter_by(dir_path=dir_path).first() is not None)
        response = self.client.post(
            self.url_for('auth.delete_visible_dir'),
            data='dir-path={}&dir-path={}&dir-path={}'.format(*delete_path_list),
            follow_redirects=True,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        self.assertTrue(response.status_code == 200)
        for dir_path in delete_path_list:
            self.assertTrue(VisibleDir.query.filter_by(dir_path=dir_path).first() is None)
