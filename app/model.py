from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import AnonymousUserMixin
from config import Permission
from app import db, login_manager
from app.path_untils import DirPath


class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(255), nullable=False, unique=True)
    user_password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return "<Users '{}'>".format(self.user_name)

    @property
    def user_password(self):
        raise AttributeError('密码不是可读属性！')

    @user_password.setter
    def user_password(self, password):
        self.user_password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.user_password_hash, password)

    @property
    def permission(self):
        if self.is_admin():
            return Permission.ADMIN
        return Permission.USER

    def is_admin(self):
        return self.user_name == 'admin'

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.user_id)


class AnonymousUser(AnonymousUserMixin):

    @property
    def permission(self):
        return Permission.ANONYMOUS_USER

    @staticmethod
    def is_admin():
        return False

    def __repr__(self):
        return '<AnonymousUser>'


class VisibleDir(db.Model):
    permission_enum = {
        'anonymous_user': 1,
        'user': 2,
        'admin': 4
    }
    permission_map = {
        1: 'anonymous_user',
        2: 'user',
        4: 'admin'
    }

    __tablename__ = 'visible_dir'
    dir_id = db.Column(db.Integer, primary_key=True)
    dir_path = db.Column(db.Text, nullable=False, unique=True)
    dir_permission = db.Column(db.Integer, nullable=False)

    def __init__(self, **kwargs):
        super(VisibleDir, self).__init__(**kwargs)

        # 携带DirPath对象
        self.p: DirPath = DirPath(self.dir_path)

        self.dir_path = self.p.path

    def __repr__(self):
        return '<VisibleDir "{}">'.format(self.dir_path)

    @property
    def permission(self):
        return self.permission_map[self.dir_permission]

    @permission.setter
    def permission(self, permission: str):
        # 检查权限值是否合法
        if permission not in self.permission_enum:
            raise ValueError('权限值只能从{}中选择！'.format(self.permission_enum.keys()))
        self.dir_permission = self.permission_enum[permission]

    def can(self, user):
        return user.permission & self.dir_permission == self.dir_permission


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


login_manager.anonymous_user = AnonymousUser
