import os
import sqlite3
from werkzeug.security import generate_password_hash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def init_database(config_class):
    # 连接数据库，同时也能在数据库不存在时创建数据库
    con = sqlite3.connect(config_class.DATABASE_PATH)
    cursor = con.cursor()

    # 建表：users
    cursor.execute("""CREATE TABLE IF NOT EXISTS `users`(
        `user_id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `user_name` VARCHAR(255) NOT NULL UNIQUE,
        `user_password_hash` VARCHAR(128) NOT NULL
    );""")
    con.commit()

    # 插入users表的管理员记录，插入前先检查管理员记录是否存在
    result = cursor.execute('SELECT count(*) FROM `users` WHERE user_name="admin";').fetchone()
    if result[0] <= 0:
        admin_password_hash = generate_password_hash(config_class.FLASK_ADMIN_PASSWORD)
        cursor.execute(
            'INSERT INTO `users`(`user_name`, `user_password_hash`) VALUES("admin", ?);',
            (admin_password_hash, )
        )
        con.commit()

    # 建表：visible_dir
    cursor.execute("""CREATE TABLE IF NOT EXISTS `visible_dir`(
        `dir_id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `dir_path` TEXT NOT NULL UNIQUE,
        `dir_permission` INT NOT NULL
    );""")
    con.commit()

    # 关闭连接
    cursor.close()
    con.close()


def create_app(config_name):
    # 选择环境
    app = Flask(__name__)
    config_class = config[config_name]
    app.config.from_object(config_class)
    config_class.init_app(app)

    # Flask扩展配置
    db.init_app(app)
    login_manager.init_app(app)

    # 初始化数据库
    init_database(config_class)

    # 注册蓝图
    from .main.views import main as main_blueprint
    from .auth.views import auth as auth_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
