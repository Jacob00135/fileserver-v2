import os.path
from urllib.parse import quote
from config import BASE_PATH, ErrorInfo
from app import db
from app.model import Users, VisibleDir
from tests.base.test_base import BaseUnittestCase
from tests.auth.untils import generate_visible_dir


class BrowseFileTestCase(BaseUnittestCase):

    def setUp(self) -> None:
        super(BrowseFileTestCase, self).setUp()
        self.user = Users(user_name='Jacob1', user_password='123456')
        db.session.add(self.user)
        db.session.commit()
        generate_visible_dir()
        self.visible_dir = {
            'anonymous_user': [],
            'user': [],
            'admin': []
        }
        for v in VisibleDir.query.all():
            self.visible_dir[v.permission].append(v)

    def test_path_param_illegal(self):
        """浏览文件系统：不合法的path查询参数"""
        # 不包含"\"
        response = self.client.get(
            self.url_for('main.index', path='1234'),
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 404)

        # 不是绝对路径
        response = self.client.get(
            self.url_for('main.index', path='.\\app'),
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 404)

    def test_no_match_path(self):
        """浏览文件系统：数据库中无匹配路径"""
        self.login('admin', '123456')
        response = self.client.get(
            self.url_for('main.index', path='C:\\'),
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 404)

    def test_no_permission_path(self):
        """浏览文件系统：无权限访问一个路径"""
        response = self.client.get(
            self.url_for('main.index', path=BASE_PATH),
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 404)

    def test_match_path(self):
        """浏览文件系统：访问成功"""
        response = self.client.get(
            self.url_for('main.index', path=os.path.realpath(os.path.join(BASE_PATH, 'app/static'))),
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)

    def test_search_file_permission(self):
        """搜索文件：无权限"""
        response = self.client.get(
            self.url_for('main.search_file', keyword='main') + '&dir-path=' + quote(BASE_PATH),
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == ErrorInfo.SEARCH_FILE_DIR_ILLEGAL)

    def test_search_file_nodir(self):
        """搜索文件：要搜索的目录路径不是目录"""
        response = self.client.get(
            self.url_for('main.search_file', keyword='main') + '&dir-path=' + quote(
                os.path.realpath(os.path.join(BASE_PATH, 'app/static/_variable.scss'))
            ),
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == ErrorInfo.SEARCH_FILE_NOT_ISDIR)

    def test_search_file_empty(self):
        """搜索文件：搜索关键字为空"""
        response = self.client.get(
            self.url_for('main.search_file') + '?dir-path=' + quote(
                os.path.realpath(os.path.join(BASE_PATH, 'app/static'))
            ),
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == ErrorInfo.SEARCH_FILE_KEYWORD_EMPTY)

    def test_search_file_no_match(self):
        """搜索文件：无匹配"""
        response = self.client.get(
            self.url_for('main.search_file', keyword='\\/:*?"<>|') + '&dir-path=' + quote(
                os.path.realpath(os.path.join(BASE_PATH, 'app/static'))
            ),
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == ErrorInfo.SEARCH_FILE_NO_MATCH)

    def test_search_file(self):
        """搜索文件：成功"""
        self.login('admin', '123456')
        response = self.client.get(
            self.url_for('main.search_file', keyword='main') + '&dir-path=' + quote(BASE_PATH),
            follow_redirects=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(len(response.json['result']) > 0)
