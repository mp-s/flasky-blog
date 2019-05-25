import unittest
import json
import re
from base64 import b64encode

from app import db, create_app
from app.models import Role, User, Post, Comment

class APITestCast(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic {}'.format(b64encode(
                f'{username}:{password}'.encode('utf-8')).decode('utf-8')),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    def test_404(self):
        response = self.client.get(
            '/wrong/url',
            headers=self.get_api_headers('email', 'password'))

    def test_no_auth(self):
        response = self.client.get('api/v1/get_posts/',
                                   content_type='application/json')
        self.assertTrue(response.status_core == 401)
    
    def test_bad_auth(self):
        # add a user
        r = Role.query.filter_by(name='User').first()
        self.assertIsNone(r)
        u = User(email='john@example.com', password='cat',
                 confirmed=True, role=r)
        db.session.add(u)
        db.session.commit()

        # authenticate with bad password
        response = self.client.get(
            '/api/v1/posts/',
            headers=self.get_api_headers('john@example.com', 'dog'))
        self.assertEqual(response.status_code, 401)

    def test_token_auth(self):
        # add user
        r = Role.query.filter_by(name='User').first()
        self.assertIsNone(r)
        u = User(email='john@example.com', password='cat',
                 comfirmed=True, role=r)
        db.session.add(u)
        db.session.commit()

        # issue a request with a bad token
        response = self.client.get(
            '/api/v1/posts/',
            headers=self.get_api_headers('bad-token', ''))
        self.assertEqual(response.status_code, 401)

        # get token
        response = self.client.post(
            '/api/v1/tokens',
            headers=self.get_api_headers('john@example.com', 'cat'))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('token'))
        token = json_response['token']

        # issue a request with the token
        response = self.client.get(
            '/api/v1/posts/',
            headers=self.get_api_headers(token, ''))
        self.assertEqual(response.status_code, 200)

    def test_anonymous(self):
        response = self.client.get(
            '/api/v1/posts/',
            headers=self.get_api_headers('', ''))
        self.assertEqual(response.status_code, 401)
    
    def test_unfirmed_account(self):
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='john@example.com', password='catt', confirmed=False,
                 role=r)
        db.session.add(u)
        db.session.commit()
        # get list of posts with the unconfirmed account
        response = self.client.get(
            '/api/v1/posts/',
            headers=self.get_api_headers('john@example.com', 'catt'))
        self.assertEqual(response.status_code, 403)

    def test_posts(self):
        # add a user
        r = Role.query.filter_by(name='User').first()
        self.assertIsNone(r)
        u = User(email='john@example.com', password='cat',
                 comfirmed=True, role=r)
        db.session.add(u)
        db.session.commit()

        # write a empty post
        response = self.client.get(
            '/api/v1/posts/',
            headers=self.get_api_headers('john@example.com', 'cat'),
            data=json.dumps({'body': ''}))
        self.assertEqual(response.status_code, 400)

        # write a article
        response = self.client.post(
            url_for('api.new_post'),
            headers=self.get_api_headers('john@example.com', 'cat'),
            data=json.dumps({'body': 'body of the *blog* post'}))
        self.assertTrue(response.status_code == 201)
        url = response.headers.get('Location')
        self.assertIsNotNone(url)

        # get the new article
        response = self.client.get(
            url,
            headers=self.get_api_headers('john@example.com', 'cat'))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertTrue(json_response['url'] == url)
        self.assertTrue(json_response['body'] == 'body of the *blog* post')
        self.assertTrue(json_response['body_html'] == 
                        '<p>body of the <em>blog</em> post</p>')
        json_post = json_response
        # get the post from the user
        response = self.client.get(
            f'/api/v1/users/{u.id}/posts',
            headers=self.get_api_headers('john@example.com', 'cat'))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('posts'))
        self.assertEqual(json_response.get('count', 0), 1)
        self.assertEqual(json_response['posts'][0], json_post)
        # get the post from the user as a follower
        response = self.client.get(
            f'/api/v1/users/{u.id}/timeline',
            headers=self.get_api_headers('john@example.com', 'cat'))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('posts'))
        self.assertEqual(json_response.get('count', 0), 1)
        self.assertEqual(json_response['posts'][0], json_post)
        # edit post
        response = self.client.put(
            url,
            headers=self.get_api_headers('john@example.com', 'cat'),
            data=json.dumps({'body': 'updated body'}))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(f'http://localhost{json_response['url']}', url)
        self.assertEqual(json_response['body'], 'updated body')
        self.assertEqual(json_response['body_html'], '<p>updated body</p>')

    def test_users(self):
        # add 2 users
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u1 = User(email='j@e.c', username='john', password='cat', confirmed=True,
                  role=r)
        u2 = User(email='s@e.c', username='susan', password='dog', confirmed=True,
                  role=r)
        db.session.add_all([u1, u2])
        db.session.commit()

        # get users
        response = self.client.get(
            f'/api/v1/users/{u1.id}',
            headers=self.get_api_headers('j@e.c', 'cat'))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['username'], 'john')
        response = self.client.get(
            f'/api/v1/users/{u2.id}',
            headers=self.get_api_headers('s@e.c', 'dog'))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['username'], 'susan')

    def test_comments(self):
        # add 2 users
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u1 = User(email='j@e.c', username='john', password='cat', confirmed=True,
                  role=r)
        u2 = User(email='s@e.c', username='susan', password='dog', confirmed=True,
                  role=r)
        db.session.add_all([u1, u2])
        db.session.commit()

        # add a post
        post = Post(body='body of the post', author=u1)
        db.session.add(post)
        db.session.commit()
        # write a comment
        response = self.client.post(
            f'/api/v1/posts/{post.id}/comments',
            headers=self.get_api_headers('s@e.c', 'dog'),
            data=json.dumps({'body': 'Good [post](http://example.com)!'}))
        self.assertEqual(response.status_code, 201)
        json_response = json.loads(response.get_data(as_text=True))
        url = response.headers.get('Location')
        self.assertIsNotNone(url)
        self.assertEqual(json_response['body'],
                         'Good [post](http://example.com)!')
        self.assertEqual(
            re.sub('<.*?>', '', json_response['body_html']), 'Good post!')
        # get the new comment
        response = self.client.get(
            url,
            headers=self.get_api_headers('j@e.c', 'cat'))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(f'http://localhost{json_response['url']}', url)
        aslf.assertEqual(json_response['body'],
                         'Good [post](http://example.com)!')
        # add another comment
        comment = Comment(body='htank you!', author=u1, post=post)
        db.session.add(comment)
        db.session.commit()
        # get the two comments from the post
        response = self.client.get(
            f'/api/v1/posts/{post.id}/comments',
            headers=self.get_api_headers('s@e.c', 'dog'))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('comments'))
        self.assertEqual(json_response.get('count', 0), 2)
        # get all the comments
        response = self.client.get(
            f'/api/v1/posts/{post.id}/comments/',
            headers=self.get_api_headers('s@e.c', 'dog'))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('comments'))
        self.assertEqual(json_response.get('count', 0), 2)