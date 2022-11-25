import os
import re
from collections import deque
from zipfile import ZipFile, ZIP_STORED, ZIP_DEFLATED, ZIP_LZMA
from collections import OrderedDict
from functools import wraps
from flask import abort
from flask_login import current_user
from sqlalchemy import and_
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


def match_visible_dir(path: str) -> DirPath or MountPath or None:
    """使用一个目录的路径匹配数据库中的可见目录"""
    # 匹配：不断用父级目录匹配数据库可见目录
    if os.path.ismount(path):
        p = MountPath(path)
    else:
        p = DirPath(path)

    while p is not None and not VisibleDir.query.filter(
            and_(VisibleDir.dir_path == p.path, VisibleDir.dir_permission <= current_user.permission)).all():
        p = p.father
    if p is None:
        return None
    return p


def get_upper_path(p: MountPath or DirPath, permission: str):
    """获取上一级路径"""
    # 当前路径已是磁盘根路径，将会转到根页面
    if p.father_path is None:
        return ''

    # 如果上一级有权限访问，则转到上一级，否则转到根页面
    temp_p = p.father
    while temp_p is not None and not VisibleDir.query.filter(
            and_(VisibleDir.dir_path == temp_p.path, VisibleDir.dir_permission <= permission)).all():
        temp_p = temp_p.father
    if temp_p is not None:
        return p.father_path
    return ''


def sort_file_list(files: list) -> list:
    """按照类型对文件列表中的文件进行排序"""
    # 创建有序字典，并将文件列表中的所有文件添加至字典中
    file_map = OrderedDict({
        'dir': [],
        'package': [],
        'video': [],
        'image': [],
        'audio': [],
        'text': [],
        'unknown': []
    })
    while files:
        file = files.pop(0)
        file_map[file.type].append(file)

    # 此时文件已按照类型进行排序，之后需要将有序字典转换成列表
    result = []
    while file_map:
        result.extend(file_map.popitem(False)[1])
    return result


def get_nav_path(p: MountPath or DirPath) -> list:
    result = []
    while p is not None:
        result.append((p.name, p.path))
        p = p.father
    return result


def check_path_query_param(path: str) -> bool:
    """检查查询参数path是否合法"""
    # 检查路径合法性
    if path.find('\\') == -1 or not os.path.isabs(path) or not os.path.exists(path):
        return False
    path = os.path.realpath(path)

    # 查询数据库中是否有匹配的可见目录
    dir_path = path
    if not os.path.isdir(path):
        dir_path = os.path.dirname(path)
    p = match_visible_dir(dir_path)
    if p is None:
        return False
    return True


def check_filename(filename: str) -> bool:
    """检查一个文件名是否合法"""
    if filename == '':
        return False
    try:
        next(re.finditer('[\\\/:*?"<>|]', filename))
    except StopIteration:
        return True
    return False


def compress_file(file_path_list: list, output_path: str, compress_type=None) -> None:
    """
    将多个文件添加到压缩包。注意！若目标压缩包已存在，会被覆盖！
    :param file_path_list: list[str]. 需要压缩的文件路径列表，可以包含目录，但是不能包含磁盘根目录
    :param output_path: str. 输出文件路径，必须以.zip结尾
    :param compress_type: str. 默认为None。只接收None、"zip"、"lzma"，对应仅存储、zip算法压缩、lzma算法压缩模式
    :return: None
    """
    # 确定参数
    if compress_type is None:
        compress = ZIP_STORED
    elif compress_type == 'zip':
        compress = ZIP_DEFLATED
    elif compress_type == 'lzma':
        compress = ZIP_LZMA
    else:
        raise ValueError('compress_type参数只接收None、"zip"、"lzma"')

    # 创建压缩文件
    with ZipFile(output_path, 'w', compress) as z:
        # 遍历要压缩的文件路径
        for file_path in file_path_list:
            # 添加文件
            if os.path.isfile(file_path):
                z.write(file_path, os.path.basename(file_path))
                continue

            # 添加目录
            root = os.path.dirname(file_path)
            for father, dir_names, filenames in os.walk(file_path):
                rel_father = os.path.relpath(father, root)

                # 防止空目录不会被添加
                if not filenames:
                    z.write(
                        filename=father,
                        arcname=rel_father
                    )
                    continue

                # 添加非空目录的文件
                for filename in filenames:
                    z.write(
                        filename=os.path.join(father, filename),
                        arcname=os.path.join(rel_father, filename)
                    )

        z.close()


def get_dir_struct(path: str) -> list:
    """获取一个目录的树形结构"""
    # 初始化队列
    result = []
    q = deque()
    q.append(DirPath(path))

    # 遍历树
    while q:
        p = q.popleft()
        result.append({
            'path': os.path.relpath(p.path, path),
            'type': p.type,
            'size': p.size
        })
        if p.type == 'dir':
            q.extend(sort_file_list(p.children))

    result[0]['path'] = path

    return result
