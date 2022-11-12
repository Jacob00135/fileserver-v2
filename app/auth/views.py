from flask import Blueprint, request, flash, redirect, jsonify, url_for
from flask_login import login_user, login_required, current_user, logout_user
from app.model import Users

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['POST'])
def login():
    # 已登录的用户不可重复登录
    if current_user.is_authenticated:
        return jsonify({'status': 0, 'message': '已登录用户不可重复登录'})

    # 获取发送登录请求时所在的页面路由
    current_url = request.form.get('current-url', '/')

    # 检查用户名
    user_name = request.form.get('user-name')
    user: Users = Users.query.filter_by(user_name=user_name).first()
    if user_name is None or user is None:
        flash('用户名不存在！')
        return redirect(current_url)

    # 检查密码
    user_password = request.form.get('user-password')
    if user_password is None or not user.verify_password(user_password):
        flash('密码错误！')
        return redirect(current_url)

    # 登录成功
    login_user(user, True)

    return redirect(current_url)


@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
