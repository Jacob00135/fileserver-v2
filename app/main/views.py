import os
import shutil
from time import sleep
from urllib.parse import quote
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, abort, send_from_directory, redirect, url_for, flash, jsonify, current_app
from flask_login import current_user, login_required
from config import ErrorInfo, Config
from app import after_response
from app.model import VisibleDir
from app.untils import get_upper_path, sort_file_list, get_nav_path, check_path_query_param, admin_required, \
    check_filename, get_dir_struct, compress_file
from app.path_untils import MountPath, DirPath, create_path_object, get_file_size

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
        nav_path=get_nav_path(p),  # 面包屑导航路径
        UPLOAD_FILE_MAX_SIZE=Config.MAX_CONTENT_LENGTH,  # 上传文件的最大字节
        UPLOAD_FILE_HINT_INFO=Config.UPLOAD_FILE_TOO_LARGE_ERROR  # 上传文件提示信息
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


@main.app_errorhandler(413)
def request_entity_too_large(e):
    return jsonify({'status': 0, 'message': ErrorInfo.UPLOAD_FILE_TOO_LARGE})


@main.route('/download')
def download():
    # 检查查询参数
    path = request.args.get('path', '', type=str)
    if not check_path_query_param(path):
        abort(404)
    path = os.path.realpath(path)

    # 响应文件
    dir_path, filename = os.path.split(path)
    if os.path.isfile(path):
        return send_from_directory(
            directory=dir_path,
            path=os.path.basename(path),
            as_attachment=True
        )

    # 检查是否是根目录
    if os.path.ismount(path):
        flash(ErrorInfo.DOWNLOAD_MOUNT)
        return redirect(url_for('main.index', path=dir_path))

    # 压缩目录
    compress_filepath = path + '.zip'
    compress_filename = os.path.basename(compress_filepath)
    compress_file(file_path_list=[path], output_path=path + '.zip', compress_type=None)

    # 分块读取文件
    def read_file():
        block_size = 1024 * 1024  # 每一块的大小，单位为字节
        with open(compress_filepath, 'rb') as file:
            block = file.read(block_size)
            while block != b'':
                yield block
                block = file.read(block_size)
            file.close()
        if os.path.exists(compress_filepath):
            try:
                os.remove(compress_filepath)
            except PermissionError:
                pass

    # 保证压缩包一定会被删除
    @current_app.after_response
    def delete_compress_file():
        if os.path.exists(compress_filepath):
            try:
                os.remove(compress_filepath)
            except PermissionError:
                pass
        after_response.callbacks.pop()

    return current_app.response_class(read_file(), headers={
        'Content-Disposition': "attachment; filename={}; filename*=UTF-8''{}".format(
            quote(secure_filename(compress_filename)),
            quote(compress_filename)
        ),
        'Content-Type': 'application/x-zip-compressed'
    })


@main.route('/remove', methods=['POST'])
@admin_required
def remove():
    path_list = request.form.getlist('path')
    if not path_list:
        abort(404)

    # 只要有一个不合法，就都不进行操作
    remove_path_list = []
    dir_path = os.path.dirname(path_list[0])
    for path in path_list:
        # 检查参数
        if not check_path_query_param(path):
            abort(404)
        path = os.path.realpath(path)

        # 要删除的是一个文件
        if os.path.isfile(path):
            remove_path_list.append(('file', path))
            continue

        # 要删除的是整个目录
        if VisibleDir.query.filter_by(dir_path=path).first() is not None or os.path.ismount(path):
            flash(ErrorInfo.REMOVE_ROOT)
            return redirect(url_for('main.index', path=dir_path))
        remove_path_list.append(('dir', path))

    # 逐个删除
    for file_type, path in remove_path_list:
        if file_type == 'file':
            try:
                os.remove(path)
            except Exception as e:
                flash(ErrorInfo.REMOVE_UNKNOWN.format(e.args[0]))
                return redirect(url_for('main.index', path=dir_path))
        else:
            try:
                shutil.rmtree(path)
            except Exception as e:
                flash(ErrorInfo.REMOVE_UNKNOWN.format(e.args[0]))
                return redirect(url_for('main.index', path=dir_path))
    return redirect(url_for('main.index', path=dir_path))


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
    new_path = os.path.abspath(os.path.join(dir_path, new_filename))
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

    # 重命名目录
    if VisibleDir.query.filter_by(dir_path=path).first() is not None or os.path.ismount(path):
        flash(ErrorInfo.RENAME_ROOT)
        return redirect(url_for('main.index', path=dir_path))
    try:
        os.rename(path, new_path)
    except Exception as e:
        flash(ErrorInfo.RENAME_UNKNOWN.format(e.args[0]))
    return redirect(url_for('main.index', path=dir_path))


@main.route('/move', methods=['POST'])
@admin_required
def move():
    # 检查原路径
    path = request.form.get('source-file-path', '', type=str)
    if not check_path_query_param(path):
        abort(404)
    path = os.path.realpath(path)

    # 获取文件所在目录
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
    target_file_path = os.path.abspath(os.path.join(target_path, os.path.basename(path)))
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

    # 移动目录
    if VisibleDir.query.filter_by(dir_path=path).first() is not None or os.path.ismount(path):
        flash(ErrorInfo.MOVE_ROOT)
        return redirect(url_for('main.index', path=dir_path))
    try:
        shutil.move(path, target_file_path)
    except Exception as e:
        flash(ErrorInfo.MOVE_UNKNOWN.format(e.args[0]))
    return redirect(url_for('main.index', path=dir_path))


@main.route('/copy_file', methods=['POST'])
@admin_required
def copy_file():
    # 检查原路径
    path = request.form.get('source-file-path', '', type=str)
    if not check_path_query_param(path):
        abort(404)
    path = os.path.realpath(path)

    # 获取文件的源目录
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
    target_file_path = os.path.abspath(os.path.join(target_path, os.path.basename(path)))
    if os.path.exists(target_file_path):
        flash(ErrorInfo.COPY_TARGET_EXISTS_FILE)
        return redirect(url_for('main.index', path=dir_path))

    # 复制文件
    if os.path.isfile(path):
        try:
            shutil.copy(path, target_file_path)
        except Exception as e:
            flash(ErrorInfo.COPY_UNKNOWN.format(e.args[0]))
        return redirect(url_for('main.index', path=dir_path))

    # 复制目录
    if os.path.ismount(path):
        flash(ErrorInfo.COPY_ROOT)
        return redirect(url_for('main.index', path=dir_path))
    try:
        shutil.copytree(path, target_file_path)
    except Exception as e:
        flash(ErrorInfo.COPY_UNKNOWN.format(e.args[0]))
    return redirect(url_for('main.index', path=dir_path))


@main.route('/upload_file', methods=['POST'])
@login_required
def upload_file():
    # 检查目录路径
    path = request.form.get('path', '', type=str)
    if not check_path_query_param(path) or not os.path.isdir(path):
        return jsonify({'status': 0, 'message': ErrorInfo.UPLOAD_DIR_ILLEGAL})
    path = os.path.realpath(path)

    # 检查文件
    file = request.files.get('file')
    if file is None:
        return jsonify({'status': 0, 'message': ErrorInfo.UPLOAD_NO_FILE})
    filename = file.filename
    if not check_filename(filename):
        return jsonify({'status': 0, 'message': ErrorInfo.UPLOAD_FILENAME_ILLEGAL})
    file_path = os.path.abspath(os.path.join(path, filename))
    if os.path.exists(file_path):
        return jsonify({'status': 0, 'message': ErrorInfo.UPLOAD_FILE_EXISTS})

    # 保存文件
    file.save(file_path)

    return {'status': 1}


@main.route('/create_dir', methods=['POST'])
@admin_required
def create_dir():
    # 检查目录路径
    path = request.form.get('path', '', type=str)
    if not check_path_query_param(path) or not os.path.isdir(path):
        abort(404)
    path = os.path.realpath(path)

    # 检查目录名称
    dir_name = request.form.get('dir-name', '', type=str)
    if dir_name == '' or not check_filename(dir_name):
        flash(ErrorInfo.CREATE_DIR_NAME_ILLEGAL)
        return redirect(url_for('main.index', path=path))
    dir_path = os.path.abspath(os.path.join(path, dir_name))
    if os.path.exists(dir_path):
        flash(ErrorInfo.CREATE_DIR_EXISTS)
        return redirect(url_for('main.index', path=path))

    # 创建目录
    try:
        os.mkdir(dir_path)
    except Exception as e:
        flash(ErrorInfo.CREATE_DIR_UNKNOWN.format(e.args[0]))
    return redirect(url_for('main.index', path=path))


@main.route('/dir_size')
@login_required
def dir_size():
    # 检查目录路径
    path = request.args.get('path', '', type=str)
    if not check_path_query_param(path):
        return jsonify({
            'status': 0,
            'message': ErrorInfo.DIR_SIZE_ILLEGAL
        })
    path = os.path.realpath(path)

    # 检查是否是目录，是否是根路径
    if not os.path.isdir(path):
        return jsonify({
            'status': 0,
            'message': ErrorInfo.DIR_SIZE_NOT_ISDIR
        })
    if os.path.ismount(path):
        return jsonify({
            'status': 0,
            'message': ErrorInfo.DIR_SIZE_MOUNT
        })

    # 计算目录大小
    total = 0
    for father, dir_names, filenames in os.walk(path):
        for filename in filenames:
            total = total + os.path.getsize(os.path.join(father, filename))
    result = get_file_size(total)

    return jsonify({
        'status': 1,
        'result': result
    })


@main.route('/preview_dir')
def preview_dir():
    # 检查查询参数
    path = request.args.get('path', '', type=str)
    if not check_path_query_param(path):
        return jsonify({
            'status': 0,
            'message': ErrorInfo.PREVIEW_DIR_ILLEGAL
        })
    path = os.path.realpath(path)

    # 检查是否是目录路径
    if not os.path.isdir(path):
        return jsonify({
            'status': 0,
            'message': ErrorInfo.PREVIEW_DIR_NOT_ISDIR
        })

    # 响应目录结构
    return jsonify({
        'status': 1,
        'result': get_dir_struct(path)
    })
