import os


BASE_PATH = os.path.abspath(os.path.dirname(__file__))
DATABASE_DIR_PATH = os.path.join(BASE_PATH, 'app/database_sqlite')


class Config(object):
    # 密钥
    SECRET_KEY = os.urandom(16)

    # 管理员用户和密码
    FLASK_ADMIN_USERNAME = 'admin'

    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 上传文件相关
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024 * 1024  # 限制上传文件的大小为2GB

    # 用户名不允许出现的字符
    USER_NAME_ILLEGAL_CHAR = '[^a-zA-Z0-9@()_-]'

    # 密码不允许出现的字符
    USER_PASSWORD_ILLEGAL_CHAR = '[^a-zA-Z0-9@()_-]'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True
    DATABASE_PATH = os.path.join(DATABASE_DIR_PATH, 'db.sqlite')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DATABASE_PATH)
    FLASK_ADMIN_PASSWORD = os.environ.get('FLASK_ADMIN_PASSWORD')


class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False
    DATABASE_PATH = os.path.join(DATABASE_DIR_PATH, 'db.sqlite')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DATABASE_PATH)
    FLASK_ADMIN_PASSWORD = os.environ.get('FLASK_ADMIN_PASSWORD')


class TestingConfig(Config):
    TESTING = True
    DATABASE_PATH = os.path.join(DATABASE_DIR_PATH, 'db_test.sqlite')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DATABASE_PATH)
    FLASK_ADMIN_PASSWORD = '123456'


class ErrorInfo(object):
    # 用户信息相关
    USER_NAME_NULL = '用户名不能为空！'
    USER_NOT_EXISTS = '用户名不存在！'
    USER_NAME_ILLEGAL = '用户名不合法：只能是数字字母和@()_-，且长度是6~16'
    USER_LOGGED = '已登录用户不可重复登录'
    USER_PASSWORD_NULL = '密码不能为空！'
    USER_PASSWORD_WRONG = '密码错误'
    USER_PASSWORD_ILLEGAL = '密码不合法：只能是数字字母和@()_-，且长度是6~16'
    USER_PASSWORD_SAME = '不能与原密码一样！'


class UserNameError(object):
    ILLEGAL_CHAR = Config.USER_NAME_ILLEGAL_CHAR
    NULL_ERROR = ErrorInfo.USER_NAME_NULL
    ILLEGAL_ERROR = ErrorInfo.USER_NAME_ILLEGAL


class UserPasswordError(object):
    ILLEGAL_CHAR = Config.USER_PASSWORD_ILLEGAL_CHAR
    NULL_ERROR = ErrorInfo.USER_PASSWORD_NULL
    ILLEGAL_ERROR = ErrorInfo.USER_PASSWORD_ILLEGAL


config = {
    'default': DevelopmentConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
