import os
import shutil
from flask import Blueprint, render_template, request, abort, send_from_directory, redirect, url_for, flash
from flask_login import current_user
from config import ErrorInfo
from app.model import VisibleDir
from app.untils import get_upper_path, sort_file_list, get_nav_path, check_path_query_param, admin_required, \
    check_filename
from app.path_untils import MountPath, DirPath, create_path_object

main = Blueprint('main', __name__)


@main.route('/')
def index():
    # 访问无查询参数主页
    path = request.args.get('path', '', type=str)
    if path == '':
        visible_dir_list = VisibleDir.query.filter(VisibleDir.dir_permission <= current_user.permission).all()
        path_object_list = create_path_object(visible_dir_list)
        return render_template(
            'main/index.html',
            file_list=path_object_list,  # 要展示的文件列表
            root_page=True  # 是否是根页面
        )

    # 检查查询参数path是否合法
    if not check_path_query_param(path):
        abort(404)
    path = os.path.realpath(path)

    # 响应文件
    dir_path = path
    if not os.path.isdir(path):
        dir_path = os.path.dirname(path)
    if os.path.isfile(path):
        return send_from_directory(
            directory=dir_path,
            path=os.path.basename(path),
            as_attachment=False
        )

    # 响应目录
    if os.path.ismount(path):
        p = MountPath(path)
    else:
        p = DirPath(path)
    upper_path = get_upper_path(p, current_user.permission)
    return render_template(
        'main/index.html',
        file_list=sort_file_list(p.children),  # 要展示的文件列表
        root_page=False,  # 是否是根页面
        upper_path=upper_path,  # 上一级路径
        current_dir_path=p.path,  # 当前目录绝对路径
        nav_path=get_nav_path(p)  # 面包屑导航路径
    )


@main.app_errorhandler(404)
def forbidden(e):
    return render_template('base/404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('base/500.html'), 500


@main.app_errorhandler(403)
def forbidden(e):
    return render_template('base/404.html'), 404


@main.app_errorhandler(405)
def method_not_allowed(e):
    return render_template('base/404.html'), 404


@main.route('/download')
def download():
    # 检查查询参数
    path = request.args.get('path', '', type=str)
    if not check_path_query_param(path):
        abort(404)
    path = os.path.realpath(path)

    # 响应文件
    dir_path = path
    if os.path.isfile(path):
        dir_path = os.path.dirname(path)
        return send_from_directory(
            directory=dir_path,
            path=os.path.basename(path),
            as_attachment=True
        )

    # 响应目录
    return 'response dir'


@main.route('/remove', methods=['POST'])
@admin_required
def remove():
    # 检查参数
    path = request.form.get('path', '', type=str)
    if not check_path_query_param(path):
        abort(404)
    path = os.path.realpath(path)

    # 删除文件
    dir_path = path
    if os.path.isfile(path):
        dir_path = os.path.dirname(path)
        try:
            os.remove(path)
        except Exception as e:
            flash(ErrorInfo.REMOVE_UNKNOWN.format(e.args[0]))
        return redirect(url_for('main.index', path=dir_path))

    return 'response dir'


@main.route('/rename', methods=['POST'])
@admin_required
def rename():
    # 检查绝对路径
    path = request.form.get('path', '', type=str)
    if not check_path_query_param(path):
        abort(404)
    path = os.path.realpath(path)

    # 获取文件所在目录及文件名
    dir_path, filename = os.path.split(path)

    # 检查是否新旧名称相同
    new_filename = request.form.get('new-file-name', '', type=str)
    if filename == new_filename:
        flash(ErrorInfo.RENAME_FILENAME_SAME)
        return redirect(url_for('main.index', path=dir_path))

    # 检查新名称是否合法
    if not check_filename(new_filename):
        flash(ErrorInfo.RENAME_NEW_FILENAME_ILLEGAL)
        return redirect(url_for('main.index', path=dir_path))

    # 检查同目录下是否已有同名文件
    new_path = os.path.realpath(os.path.join(dir_path, new_filename))
    if os.path.exists(new_path):
        flash(ErrorInfo.RENAME_FILE_EXISTS)
        return redirect(url_for('main.index', path=dir_path))

    # 重命名文件
    if os.path.isfile(path):
        try:
            os.rename(path, new_path)
        except Exception as e:
            flash(ErrorInfo.RENAME_UNKNOWN.format(e.args[0]))
        return redirect(url_for('main.index', path=dir_path))

    return 'response dir'


@main.route('/move', methods=['POST'])
@admin_required
def move():
    # 检查原路径
    path = request.form.get('source-file-path', '', type=str)
    if not check_path_query_param(path):
        abort(404)
    path = os.path.realpath(path)

    # 获取文件的源目录
    dir_path = path
    if os.path.isfile(path):
        dir_path = os.path.dirname(path)

    # 检查目标路径：是否是绝对路径、路径是否存在、是否是目录路径、目标路径下是否已有同名文件
    target_path = request.form.get('target-file-path', '', type=str)
    if target_path.find('\\') == -1 or not os.path.isabs(target_path):
        flash(ErrorInfo.MOVE_TARGET_NOT_ISABS)
        return redirect(url_for('main.index', path=dir_path))
    if not os.path.exists(target_path):
        flash(ErrorInfo.MOVE_TARGET_NOT_EXISTS)
        return redirect(url_for('main.index', path=dir_path))
    target_path = os.path.realpath(target_path)
    if not os.path.isdir(target_path):
        flash(ErrorInfo.MOVE_TARGET_NOT_ISDIR)
        return redirect(url_for('main.index', path=dir_path))
    target_file_path = os.path.realpath(os.path.join(target_path, os.path.basename(path)))
    if os.path.exists(target_file_path):
        flash(ErrorInfo.MOVE_TARGET_EXISTS_FILE)
        return redirect(url_for('main.index', path=dir_path))

    # 移动文件
    if os.path.isfile(path):
        try:
            shutil.move(path, target_file_path)
        except Exception as e:
            flash(ErrorInfo.MOVE_UNKNOWN.format(e.args[0]))
        return redirect(url_for('main.index', path=dir_path))

    return 'move dir'


@main.route('/copy_file', methods=['POST'])
@admin_required
def copy_file():
    # 检查原路径
    path = request.form.get('source-file-path', '', type=str)
    if not check_path_query_param(path):
        abort(404)
    path = os.path.realpath(path)

    # 获取文件的源目录
    dir_path = path
    if os.path.isfile(path):
        dir_path = os.path.dirname(path)

    # 检查目标路径：是否是绝对路径、路径是否存在、是否是目录路径、目标路径下是否已有同名文件
    target_path = request.form.get('target-file-path', '', type=str)
    if target_path.find('\\') == -1 or not os.path.isabs(target_path):
        flash(ErrorInfo.COPY_TARGET_NOT_ISABS)
        return redirect(url_for('main.index', path=dir_path))
    if not os.path.exists(target_path):
        flash(ErrorInfo.COPY_TARGET_NOT_EXISTS)
        return redirect(url_for('main.index', path=dir_path))
    target_path = os.path.realpath(target_path)
    if not os.path.isdir(target_path):
        flash(ErrorInfo.COPY_TARGET_NOT_ISDIR)
        return redirect(url_for('main.index', path=dir_path))
    target_file_path = os.path.realpath(os.path.join(target_path, os.path.basename(path)))
    if os.path.exists(target_file_path):
        flash(ErrorInfo.COPY_TARGET_EXISTS_FILE)
        return redirect(url_for('main.index', path=dir_path))

    # 移动文件
    if os.path.isfile(path):
        try:
            shutil.copy(path, target_file_path)
        except Exception as e:
            flash(ErrorInfo.COPY_UNKNOWN.format(e.args[0]))
        return redirect(url_for('main.index', path=dir_path))

    return 'move dir'
