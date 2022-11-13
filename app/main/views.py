from flask import Blueprint, render_template

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('main/index.html')


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
