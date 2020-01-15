import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    ''' 通常配置 '''
    # 密钥 web 表单用(flask-wtf)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

    # 邮箱
    FLASKY_MAIL_SUBJECT_PREFIX = '[flask demo]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')  # email收件人
    # 页面显示数的配置
    FLASKY_POSTS_PER_PAGE = 20
    FLASKY_FOLLOWERS_PER_PAGE = 20
    FLASKY_COMMENTS_PER_PAGE = 20

    ''' 如果设置成 True (默认情况)，
    Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。
    这需要额外的内存， 如果不必要的可以禁用它。'''
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 启用缓慢查询记录功能配置
    SQLALCHEMY_RECORD_QUERIES = True
    FLASKY_SLOW_DB_QUERY_TIME = 0.5

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    ''' 开发环境配置 '''
    DEBUG = True

    # mail config
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USER_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestConfig(Config):
    ''' 测试环境配置 '''
    TESTING = True
    # 测试配置禁用 csrf 保护
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    ''' 生产环境配置 '''
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    @staticmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the admin
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
                                   fromaddr=cls.FLASKY_MAIL_SENDER,
                                   toaddrs=[cls.FLASKY_ADMIN],
                                   subject=cls.FLASKY_MAIL_SUBJECT_PREFIX +
                                   'Applicaiton error',
                                   credentials=credentials,
                                   secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}