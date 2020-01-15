from flask import render_template, request, jsonify
from . import main
'''蓝本中编写错误处理程序
app_errorhandler 作用域: 整个程序
errorhandler 作用域: 蓝本中
'''


@main.app_errorhandler(403)
def forbidden(e):
    # REST 接口错误处理
    if (request.accept_mimetypes.accept_json
            and not request.accept_mimetypes.accept_html):
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response

    return render_template('403.html'), 403


@main.app_errorhandler(404)
def page_not_found(e):
    # REST 接口错误处理
    if (request.accept_mimetypes.accept_json
            and not request.accept_mimetypes.accept_html):
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response

    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    # REST 接口错误处理
    if (request.accept_mimetypes.accept_json
            and not request.accept_mimetypes.accept_html):
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response

    return render_template('500.html'), 500
