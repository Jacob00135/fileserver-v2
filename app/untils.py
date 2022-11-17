import os
import re
from functools import wraps
from flask import abort
from flask_login import current_user
from config import ErrorInfo, UserNameError, UserPasswordError
from app import db
from app.model import Users


def check_legal(string: str, check_type: str) -> dict:
    """检查用户名/密码是否是合法的"""
    # 检查参数
    if check_type == 'user_name':
        error_obj = UserNameError
    elif check_type == 'user_password':
        error_obj = UserPasswordError
    else:
        raise ValueError('check_type只能是`user_name`或`user_password`')

    # 是否为空
    if string == '':
        return {'legal': False, 'error_info': error_obj.NULL_ERROR}

    # 长度合法性
    length = len(string)
    if length < 6 or length > 16:
        return {'legal': False, 'error_info': error_obj.ILLEGAL_ERROR}

    # 内容合法性
    match_iter = re.finditer(error_obj.ILLEGAL_CHAR, string)
    try:
        next(match_iter)
    except StopIteration:
        pass
    else:
        return {'legal': False, 'error_info': error_obj.ILLEGAL_ERROR}

    return {'legal': True, 'error_info': ''}


def check_and_update_password(user: Users, password: str) -> dict:
    # 检查密码合法性
    check_result = check_legal(password, 'user_password')
    if not check_result['legal']:
        return {'success': False, 'error_info': check_result['error_info']}

    # 检查是否与原密码一样
    if user.verify_password(password):
        return {'success': False, 'error_info': ErrorInfo.USER_PASSWORD_SAME}

    # 通过检验，修改密码
    user.user_password = password
    db.session.add(user)
    db.session.commit()

    return {'success': True, 'error_info': ''}


def admin_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if not current_user.is_admin():
            abort(403)
        return func(*args, **kwargs)
    return decorator


def check_dir_path(dir_path: str) -> dict:
    """检查一个可见目录路径是否合法"""
    if (dir_path.find('/') == -1 and dir_path.find('\\') == -1) or not os.path.isabs(dir_path):
        return {'legal': False, 'error_info': ErrorInfo.VISIBLE_DIR_ABSPATH}
    dir_path = os.path.abspath(dir_path)
    if not os.path.exists(dir_path):
        return {'legal': False, 'error_info': ErrorInfo.VISIBLE_DIR_NOT_EXISTS}
    if not os.path.isdir(dir_path):
        return {'legal': False, 'error_info': ErrorInfo.VISIBLE_DIR_ISDIR}
    return {'legal': True, 'error_info': ''}
