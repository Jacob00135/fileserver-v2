from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
# TODO 使用flask-login时，需要取消下一行的注释
# login_manager.login_view = 'auth.login'


def create_app(config_name):
    # 选择环境
    app = Flask(__name__)
    env_obj = config[config_name]
    app.config.from_object(env_obj)
    env_obj.init_app(app)

    # Flask扩展配置
    db.init_app(app)
    login_manager.init_app(app)

    # 注册蓝图
    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
