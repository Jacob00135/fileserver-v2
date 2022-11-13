from flask import Blueprint, request, flash, redirect, jsonify, url_for
from flask_login import login_user, login_required, current_user, logout_user
from config import ErrorInfo
from app import db
from app.model import Users
from app.untils import check_legal

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
    current_url = request.form.get('current-url', '/')

    # 检查用户名
    user_name = request.form.get('user-name')
    user: Users = Users.query.filter_by(user_name=user_name).first()
    if user_name is None or user is None:
        flash(ErrorInfo.USER_NOT_EXISTS)
        return redirect(current_url)

    # 检查密码
    user_password = request.form.get('user-password')
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
    current_url = request.form.get('current-url', '/')

    # 检查密码合法性
    password = request.form.get('new-password', '')
    check_result = check_legal(password, 'user_password')
    if not check_result['legal']:
        flash(check_result['error_info'])
        return redirect(current_url)

    # 检查是否与原密码一样
    if current_user.verify_password(password):
        flash(ErrorInfo.USER_PASSWORD_SAME)
        return redirect(current_url)

    # 修改密码成功，需要重新登录
    current_user.user_password = password
    db.session.add(current_user)
    db.session.commit()
    logout_user()

    return redirect(url_for('main.index'))
