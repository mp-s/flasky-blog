import unittest
import threading
import re
import time
from selenium import webdriver

from app import create_app, db, fake
from app.models import Role, User, Post


class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        # start Chrome
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        try:
            cls.client = webdriver.Chrome(chrome_options=options)
        except:
            pass

        # skip test if browser could not be started
        if cls.client:
            # create the application
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            # suppress logging to keep unittest output clean
            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel('ERROR')

            # create db and fill fake data
            db.create_all()
            Role.insert_roles()
            fake.users(10)
            fake.posts(10)

            # add admin user
            admin_role = Role.query.filter_by(name='Administrator').first()
            admin = User(email='j@e.c',
                         username='john',
                         password='cat',
                         role=admin_role,
                         confirmed=True)
            db.session.add(admin)
            db.session.commit()

            # 在一个线程启动 Flask 服务器
            # threading.Thread(target=cls.app.run).start()
            cls.server_thread = threading.Thread(target=cls.app.run,
                                                 kwargs={
                                                     'debug': False,
                                                     'user_reloader': False,
                                                     'user_debugger': False
                                                 })
            cls.server_thread.start()

            time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            # 关闭 flask 服务器和浏览器
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.quit()
            cls.server_thread.join()

            # 销毁数据库
            db.drop_all()
            db.session.remove()

            # 删除程序上下文
            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass

    def test_admin_home_page(self):
        # 进入首页
        self.client.get('http://localhost:5000/')
        self.assertTrue(
            re.search('Hello,\s+Stranger!', self.client.page_source))

        # navigate to login page
        self.client.find_element_by_link_text('Log In').click()
        self.assertTrue('<h1>Login</h1>' in self.client.page_source)

        # login
        self.client.find_element_by_name('email').send_keys('j@e.c')
        self.client.find_element_by_name('password').send_keys('cat')
        self.client.find_element_by_name('submit').click()
        self.assertTrue(re.search('Hello,\s+john!', self.client.page_source))

        # navigate to profile page
        self.client.find_element_by_link_text('Profile').click()
        self.assertTrue('<h1>john</h1>' in self.client.page_source)
