import os


BASE_PATH = os.path.realpath(os.path.dirname(__file__))
DATABASE_DIR_PATH = os.path.realpath(os.path.join(BASE_PATH, 'app/database_sqlite'))
if not os.path.exists(DATABASE_DIR_PATH):
    os.mkdir(DATABASE_DIR_PATH)


class Config(object):
    # 密钥
    SECRET_KEY = os.urandom(16)

    # 管理员用户和密码
    FLASK_ADMIN_USERNAME = 'admin'

    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 上传文件相关
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024 * 1024  # 限制上传文件的大小
    UPLOAD_FILE_TOO_LARGE_ERROR = '上传的文件不能超过4GB'  # 当上传文件超过指定大小时的提示信息

    # 用户名不允许出现的字符
    USER_NAME_ILLEGAL_CHAR = '[^a-zA-Z0-9@()_-]'

    # 密码不允许出现的字符
    USER_PASSWORD_ILLEGAL_CHAR = '[^a-zA-Z0-9@()_-]'

    # 分页时，每一页能显示的条目数
    PAGE_MAX_FILE_NUMBER = int(os.environ.get('FLASK_PAGE_MAX', 20))
    print(type(PAGE_MAX_FILE_NUMBER))
    print(PAGE_MAX_FILE_NUMBER)

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
    USER_EXISTS = '用户已存在！'
    USER_NAME_ILLEGAL = '用户名不合法：只能有数字字母和@()_-，且长度是6~16'
    USER_LOGGED = '已登录用户不可重复登录'
    USER_PASSWORD_NULL = '密码不能为空！'
    USER_PASSWORD_WRONG = '密码错误'
    USER_PASSWORD_ILLEGAL = '密码不合法：只能有数字字母和@()_-，且长度是6~16'
    USER_PASSWORD_SAME = '不能与原密码一样！'

    # 可见目录管理相关
    VISIBLE_DIR_NOT_EXISTS = '目录路径不存在！'
    VISIBLE_DIR_ABSPATH = '可见目录路径必须是绝对路径！'
    VISIBLE_DIR_ISDIR = '目标路径不是目录！'
    VISIBLE_DIR_EXISTS = '可见目录已存在！'

    # 下载文件相关
    DOWNLOAD_NO_PATH = '没有选择下载的文件'
    DOWNLOAD_MOUNT = '不能下载根目录！'
    DOWNLOAD_UNKNOWN = '下载失败：有路径既不是文件也不是目录'

    # 删除文件相关
    REMOVE_UNKNOWN = '删除失败：{}'
    REMOVE_ROOT = '不能删除根目录或可见目录！'
    REMOVE_NO_PATH = '没有选择要删除的文件'

    # 文件重命名相关
    RENAME_NEW_FILENAME_ILLEGAL = '新名称不能包含\\/:*?"<>|'
    RENAME_FILENAME_SAME = '新名称与原名称相同'
    RENAME_FILE_EXISTS = '同目录下已有相同名称'
    RENAME_UNKNOWN = '重命名失败：{}'
    RENAME_ROOT = '不能对根目录或可见目录重命名！'

    # 移动文件相关
    MOVE_TARGET_NOT_ISABS = '目标路径必须是绝对路径！'
    MOVE_TARGET_NOT_EXISTS = '目标路径不存在！'
    MOVE_TARGET_NOT_ISDIR = '目标路径必须是目录！'
    MOVE_TARGET_EXISTS_FILE = '目标路径已存在同名文件！'
    MOVE_UNKNOWN = '移动失败：{}'
    MOVE_ROOT = '不能移动根目录或可见目录！'
    MOVE_NO_PATH = '没有选择要移动的文件'

    # 复制文件相关
    COPY_TARGET_NOT_ISABS = '目标路径必须是绝对路径！'
    COPY_TARGET_NOT_EXISTS = '目标路径不存在！'
    COPY_TARGET_NOT_ISDIR = '目标路径必须是目录！'
    COPY_TARGET_EXISTS_FILE = '目标路径已存在同名文件！'
    COPY_UNKNOWN = '复制失败：{}'
    COPY_ROOT = '不能复制根目录！'
    COPY_NO_PATH = '没有选择要复制的文件'

    # 上传文件相关
    UPLOAD_DIR_ILLEGAL = '要上传的目录路径不合法'
    UPLOAD_NO_FILE = '未选择文件'
    UPLOAD_FILENAME_ILLEGAL = '文件名不能包含\\/:*?"<>|'
    UPLOAD_FILE_EXISTS = '同目录下已有同名文件'
    UPLOAD_FILE_TOO_LARGE = Config.UPLOAD_FILE_TOO_LARGE_ERROR

    # 新建目录相关
    CREATE_DIR_NAME_ILLEGAL = '目录名不能包含\\/:*?"<>|'
    CREATE_DIR_EXISTS = '已有同名目录'
    CREATE_DIR_UNKNOWN = '创建目录失败：{}'

    # 查看大小相关
    DIR_SIZE_NO_PATH = '未选择文件'
    DIR_SIZE_ILLEGAL = '路径不合法'
    DIR_SIZE_MOUNT = '不能查看根目录的大小'

    # 预览目录相关
    PREVIEW_DIR_ILLEGAL = '目录路径不合法'
    PREVIEW_DIR_NOT_ISDIR = '不是目录'

    # 多选压缩文件相关
    COMPRESS_NO_FILEPATH = '未输入文件名'
    COMPRESS_ROOT = '不能压缩根目录'
    COMPRESS_FILENAME_ILLEGAL = '文件名不能包含\\/:*?"<>|'
    COMPRESS_FILE_EXISTS = '同名压缩包已存在！'
    COMPRESS_TYPE_ERROR = '压缩文件算法只能是`仅存储`、`zip`、`lzma`'

    # 搜索文件
    SEARCH_FILE_DIR_ILLEGAL = '没有权限访问'
    SEARCH_FILE_NOT_ISDIR = '不能在非目录路径下进行搜索！'
    SEARCH_FILE_KEYWORD_EMPTY = '搜索关键字不能为空！'
    SEARCH_FILE_NO_MATCH = '无匹配结果'


class UserNameError(object):
    ILLEGAL_CHAR = Config.USER_NAME_ILLEGAL_CHAR
    NULL_ERROR = ErrorInfo.USER_NAME_NULL
    ILLEGAL_ERROR = ErrorInfo.USER_NAME_ILLEGAL


class UserPasswordError(object):
    ILLEGAL_CHAR = Config.USER_PASSWORD_ILLEGAL_CHAR
    NULL_ERROR = ErrorInfo.USER_PASSWORD_NULL
    ILLEGAL_ERROR = ErrorInfo.USER_PASSWORD_ILLEGAL


class Permission(object):
    ANONYMOUS_USER = 1
    USER = 3
    ADMIN = 7


config = {
    'default': DevelopmentConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
