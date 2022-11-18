import os
from flask import Blueprint, render_template, request, abort, send_from_directory
from flask_login import current_user
from app.model import VisibleDir
from app.untils import match_visible_dir, get_upper_path, sort_file_list, get_nav_path
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

    # 检查路径合法性
    if path.find('\\') == -1 or not os.path.isabs(path) or not os.path.exists(path):
        abort(404)
    path = os.path.realpath(path)

    # 查询数据库中是否有匹配的可见目录
    dir_path = path
    if not os.path.isdir(path):
        dir_path = os.path.dirname(path)
    p = match_visible_dir(dir_path, current_user.permission)
    if p is None:
        abort(404)

    # 响应文件
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
