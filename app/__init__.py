from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown
from config import config

bootstrap = Bootstrap()  # bootstrap 框架
mail = Mail()
moment = Moment()  # 日期和时间 Moment.js
db = SQLAlchemy()

login_manager = LoginManager()
# 可能会有 session 异常, 导致用户登录无法记住
# login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'  # 设置登录页面端点

pagedown = PageDown()


# 工厂函数
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 初始化扩展程序
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    # 注册主蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # 注册身份验证蓝本
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # 注册 API 蓝本
    from .api_1_0 import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    # 输出配置好 Flask() 实例 app
    return app