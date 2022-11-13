from string import ascii_letters, digits
from random import randint, choices
from app import db
from app.model import Users
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


if __name__ == '__main__':
    with app.app_context():
        generate_user(10)
