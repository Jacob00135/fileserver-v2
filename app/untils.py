import os
import re
from functools import wraps
from flask import abort
from flask_login import current_user
from config import ErrorInfo, UserNameError, UserPasswordError
from app import db
from app.model import Users, VisibleDir
from app.path_untils import MountPath, DirPath


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


def match_visible_dir(path: str, permission: str) -> DirPath or MountPath or None:
    """使用一个目录的路径匹配数据库中的可见目录"""
    # 生成路径哈希表
    visible_dir_list = VisibleDir.query.filter(VisibleDir.dir_permission <= permission).all()
    path_set = set()
    for visible_dir in visible_dir_list:
        path_set.add(visible_dir.dir_path)

    # 匹配：不断用父级目录匹配数据库可见目录
    if os.path.ismount(path):
        p = MountPath(path)
    else:
        p = DirPath(path)
    while p is not None and p.path not in path_set:
        p = p.father
    if p is None:
        return None
    return p


def get_upper_path(p: MountPath or DirPath, permission: str):
    """获取上一级路径"""
    # 生成路径哈希表
    visible_dir_list = VisibleDir.query.filter(VisibleDir.dir_permission <= permission).all()
    path_set = set()
    for visible_dir in visible_dir_list:
        path_set.add(visible_dir.dir_path)

    # 当前路径已是磁盘根路径，将会转到根页面
    if p.father_path is None:
        return ''
    
    # 如果上一级有权限访问，则转到上一级，否则转到根页面
    temp_p = p.father
    while temp_p is not None and temp_p.path not in path_set:
        temp_p = temp_p.father
    if temp_p is not None:
        return p.father_path
    return ''
