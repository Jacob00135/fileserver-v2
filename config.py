import os


BASE_PATH = os.path.abspath(os.path.dirname(__file__))
DATABASE_DIR_PATH = os.path.join(BASE_PATH, 'app/database_sqlite')


class Config(object):
    # 密钥
    SECRET_KEY = os.urandom(16)

    # 管理员用户和密码
    FLASK_ADMIN_USERNAME = 'admin'
    FLASK_ADMIN_PASSWORD = os.environ.get('FLASK_ADMIN_PASSWORD')

    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 上传文件相关
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024 * 1024  # 限制上传文件的大小为2GB

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True
    DATABASE_PATH = os.path.join(DATABASE_DIR_PATH, 'db.sqlite')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DATABASE_PATH)


class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False
    DATABASE_PATH = os.path.join(DATABASE_DIR_PATH, 'db.sqlite')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DATABASE_PATH)


class TestingConfig(Config):
    TESTING = True
    DATABASE_PATH = os.path.join(DATABASE_DIR_PATH, 'db_test.sqlite')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DATABASE_PATH)


config = {
    'default': DevelopmentConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
