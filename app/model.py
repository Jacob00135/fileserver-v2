from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import AnonymousUserMixin
from app import db, login_manager


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

    @staticmethod
    def is_admin():
        return False


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


login_manager.anonymous_user = AnonymousUser
