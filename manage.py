#!usr/bin/env python3
import os
import sys
import click

# 添加覆盖度检测
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

from app import create_app, db
from app.models import User, Role, Permission, Post, Follow, Comment
from flask_migrate import Migrate, upgrade

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


# 添加 shell 上下文, 集成 python shell
@app.shell_context_processor
def make_shell_context():
    return dict(app=app,
                db=db,
                User=User,
                Follow=Follow,
                Role=Role,
                Permission=Permission,
                Post=Post,
                Comment=Comment)


# manager 改用 click 库
@app.cli.command()
@click.option('--coverage/--no-coverage',
              default=False,
              help='Run tests under coverage.')
@click.argument('test_names', nargs=-1)
def test(coverage, test_names):
    ''' Run the unit tests. '''
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import subprocess
        os.environ['FLASK_COVERAGE'] = '1'
        sys.exit(subprocess.call(sys.argv))
        # os.execvp(sys.executable, [sys.executable] + sys.argv)

    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp', 'coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://{}/index.html'.format(covdir))
        COV.erase()


@app.cli.command()
@click.option('--length',
              default=25,
              help='Number of functions to include in the profiler report.')
@click.option('--profile-dir',
              default=None,
              help='Directory where profiler data files are saved.')
def profile(length, profile_dir):
    ''' Start the application under the code profiler. '''
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app,
                                      restrictions=[length],
                                      profile_dir=profile_dir)

    # flask 1.0 bug: 不能自定义 app.run 启动位置, 解决方案一:
    os.environ['FLASK_RUN_FROM_CLI'] = "false"
    app.run()
    # 解决方案二:
    # from werkzeug.serving import run_simple
    # run_simple('127.0.0.1', 5000, app, use_debugger=False)


@app.cli.command()
def deploy():
    """ Run deployment tasks. """

    # 把数据库迁移到最新修订版本
    upgrade()

    # 创建用户角色
    Role.insert_roles()

    # 所有用户关注此用户
    User.add_self_follows()


# if __name__ == '__main__':
#     app.run()
