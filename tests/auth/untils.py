import os
from string import ascii_letters, digits
from random import randint, choices
from config import BASE_PATH
from app import db
from app.model import Users, VisibleDir
from file_server import app

legal_char = ascii_letters + digits + '@()_-'


def generate_user(generate_num: int) -> None:
    """生成用户"""
    i = 0
    while i < generate_num:
        # 随机生成用户名
        user_name = ''.join(choices(legal_char, k=randint(6, 16)))

        # 检查用户名是否已存在
        if Users.query.filter_by(user_name=user_name).first() is not None:
            continue

        # 添加用户
        user = Users(user_name=user_name, user_password='123456')
        db.session.add(user)

        i = i + 1

    db.session.commit()


def generate_visible_dir():
    """生成可见目录"""
    visible_dir_list = [
        VisibleDir(
            dir_path=BASE_PATH,
            permission='admin',
        ),
        VisibleDir(
            dir_path=os.path.join(BASE_PATH, 'admin_dir'),
            permission='admin'
        ),
        VisibleDir(
            dir_path=os.path.join(BASE_PATH, 'app/database_sqlite'),
            permission='admin'
        ),
        VisibleDir(
            dir_path=os.path.join(BASE_PATH, 'app/auth'),
            permission='user'
        ),
        VisibleDir(
            dir_path=os.path.join(BASE_PATH, 'app/main'),
            permission='user'
        ),
        VisibleDir(
            dir_path=os.path.join(BASE_PATH, 'app/static'),
            permission='anonymous_user'
        ),
        VisibleDir(
            dir_path=os.path.join(BASE_PATH, 'tests'),
            permission='admin'
        ),
        VisibleDir(
            dir_path=os.path.join(BASE_PATH, 'app/templates'),
            permission='anonymous_user'
        ),
        VisibleDir(
            dir_path=os.path.join(BASE_PATH, 'app'),
            permission='admin'
        )
    ]
    for visible_dir in visible_dir_list:
        if VisibleDir.query.filter_by(dir_path=visible_dir.dir_path).first() is None:
            db.session.add(visible_dir)
    db.session.commit()


def delete_all_visible_dir():
    for visible_dir in VisibleDir.query.all():
        db.session.delete(visible_dir)
    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        generate_visible_dir()
