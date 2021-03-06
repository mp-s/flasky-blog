from flask import g, jsonify
# from flask_login import AnonymousUserMixin
from flask_httpauth import HTTPBasicAuth
from ..models import User
from . import api
from .errors import unauthorized, forbidden

auth = HTTPBasicAuth()


# 验证密码或令牌的回调
@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        # g.current_user = AnonymousUserMixin()
        # return True
        # 关掉未登录访问
        return False
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None

    user = User.query.filter_by(email=email_or_token.lower()).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


# flask-httpauth 错误处理程序
@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


# 生成身份验证令牌
@api.route('/tokens/', methods=['POST'])
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({
        'token': g.current_user.generate_auth_token(expiration=3600),
        'expiration': 3600
    })
