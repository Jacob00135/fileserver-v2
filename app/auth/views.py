import os
from flask import Blueprint, request, flash, redirect, jsonify, url_for, render_template
from flask_login import login_user, login_required, current_user, logout_user
from config import ErrorInfo
from app import db
from app.model import Users, VisibleDir
from app.untils import check_legal, check_and_update_password, admin_required, check_dir_path

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    # 因为没有登录页面，所以当请求登录页面时，重定向到首页
    if request.method == 'GET':
        return redirect(url_for('main.index'))

    # 已登录的用户不可重复登录
    if current_user.is_authenticated:
        return jsonify({
            'status': 0,
            'message': ErrorInfo.USER_LOGGED
        })

    # 获取发送登录请求时所在的页面路由
    current_url = request.form.get('current-url', '/', type=str)

    # 检查用户名
    user_name = request.form.get('user-name', '', type=str)
    user: Users = Users.query.filter_by(user_name=user_name).first()
    if user_name is None or user is None:
        flash(ErrorInfo.USER_NOT_EXISTS)
        return redirect(current_url)

    # 检查密码
    user_password = request.form.get('user-password', '', type=str)
    if user_password is None or not user.verify_password(user_password):
        flash(ErrorInfo.USER_PASSWORD_WRONG)
        return redirect(current_url)

    # 登录成功
    login_user(user, True)

    return redirect(current_url)


@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/update_password', methods=['POST'])
@login_required
def update_password():
    # 获取发送登录请求时所在的页面路由
    current_url = request.form.get('current-url', '/', type=str)

    # 修改密码
    password = request.form.get('new-password', '', type=str)
    update_result = check_and_update_password(current_user, password)
    if not update_result['success']:
        flash(update_result['error_info'])
        return redirect(current_url)

    # 修改密码成功，需要重新登录
    logout_user()

    return redirect(url_for('main.index'))


@auth.route('/user_manage')
@admin_required
def user_manage():
    # 查询所有用户，除了管理员
    users = Users.query.filter(Users.user_name != 'admin').all()
    users = list(reversed(users))

    return render_template('auth/user_manage.html', users=users)


@auth.route('/add_user', methods=['POST'])
@admin_required
def add_user():
    # 检查用户名
    user_name = request.form.get('user-name', '', type=str)
    check_result = check_legal(user_name, 'user_name')
    if not check_result['legal']:
        flash(check_result['error_info'])
        return redirect(url_for('auth.user_manage'))

    # 检查相同用户名的用户是否已存在
    if Users.query.filter_by(user_name=user_name).first() is not None:
        flash(ErrorInfo.USER_EXISTS)
        return redirect(url_for('auth.user_manage'))

    # 检查密码
    user_password = request.form.get('user-password', '', type=str)
    check_result = check_legal(user_password, 'user_password')
    if not check_result['legal']:
        flash(check_result['error_info'])
        return redirect(url_for('auth.user_manage'))

    # 检查通过，添加用户
    user = Users(user_name=user_name, user_password=user_password)
    db.session.add(user)
    db.session.commit()

    return redirect(url_for('auth.user_manage'))


@auth.route('/delete_user', methods=['POST'])
@admin_required
def delete_user():
    # 需要考虑批量删除的情况：只要有1个不合法，就全都不删除
    delete_users = []
    for user_name in request.form.getlist('user-name'):
        # 检查用户是否存在
        user = Users.query.filter_by(user_name=user_name).first()
        if user is None:
            flash(ErrorInfo.USER_NOT_EXISTS)
            return redirect(url_for('auth.user_manage'))

        # 检查通过，加入待删除列表
        delete_users.append(user)

    # 删除用户
    for user in delete_users:
        db.session.delete(user)
        db.session.commit()

    return redirect(url_for('auth.user_manage'))


@auth.route('/update_user_password', methods=['POST'])
@admin_required
def update_user_password():
    # 检查用户是否存在
    user_name = request.form.get('user-name', '', type=str)
    user = Users.query.filter_by(user_name=user_name).first()
    if user is None:
        flash(ErrorInfo.USER_NOT_EXISTS)
        return redirect(url_for('auth.user_manage'))

    # 检查密码
    password = request.form.get('new-password', '', type=str)
    update_result = check_and_update_password(user, password)
    if not update_result['success']:
        flash(update_result['error_info'])
    return redirect(url_for('auth.user_manage'))


@auth.route('/visible_dir_manage')
@admin_required
def visible_dir_manage():
    # 查询所有可见目录，并根据访问权限进行分类
    visible_dir_list: list[VisibleDir] = VisibleDir.query.all()
    visible_dir_dict = {
        'anonymous_user': [],
        'user': [],
        'admin': []
    }
    for visible_dir in visible_dir_list:
        user_classes = visible_dir.permission
        visible_dir_dict[user_classes].append(visible_dir)

    return render_template('auth/visible_dir.html', visible_dir_dict=visible_dir_dict)


@auth.route('/add_visible_dir', methods=['POST'])
@admin_required
def add_visible_dir():
    # 检查可见目录路径
    dir_path = request.form.get('dir-path', '', type=str)
    check_result = check_dir_path(dir_path)
    if not check_result['legal']:
        flash(check_result['error_info'])
        return redirect(url_for('auth.visible_dir_manage'))

    # 检查可见目录是否已存在
    dir_path = os.path.realpath(dir_path)
    if VisibleDir.query.filter_by(dir_path=dir_path).first() is not None:
        flash(ErrorInfo.VISIBLE_DIR_EXISTS)
        return redirect(url_for('auth.visible_dir_manage'))

    # 检查权限值
    visible_dir = VisibleDir(dir_path=dir_path)
    try:
        visible_dir.permission = request.form.get('permission', '', type=str)
    except ValueError as e:
        flash(e.args[0])
        return redirect(url_for('auth.visible_dir_manage'))

    # 检查通过，添加到数据库
    db.session.add(visible_dir)
    db.session.commit()

    return redirect(url_for('auth.visible_dir_manage'))


@auth.route('/delete_visible_dir', methods=['POST'])
@admin_required
def delete_visible_dir():
    # 需要考虑批量删除的情况：只要有1个不合法，就全都不删除
    delete_visible_dir_list = []
    for dir_path in request.form.getlist('dir-path'):
        # 检查可见目录是否存在
        visible_dir = VisibleDir.query.filter_by(dir_path=dir_path).first()
        if visible_dir is None:
            flash(ErrorInfo.VISIBLE_DIR_NOT_EXISTS)
            return redirect(url_for('auth.visible_dir_manage'))

        # 检查通过，加入待删除列表
        delete_visible_dir_list.append(visible_dir)

    # 删除用户
    for visible_dir in delete_visible_dir_list:
        db.session.delete(visible_dir)
        db.session.commit()

    return redirect(url_for('auth.visible_dir_manage'))
