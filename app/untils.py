import re
from config import UserNameError, UserPasswordError


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
