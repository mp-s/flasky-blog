from flask import Flask, request, make_response, redirect, abort
from flask_script import Manager


app = Flask(__name__)
manager = Manager(app)

@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent')
    return '<h1>Your Browser is: {}</h1>'.format(user_agent)

    # return '<h1>Bad Request</h1>', 400

    # response = make_response('<h1>This document carries a cookie!</h1>')
    # response.set_cookie('answer', '42')
    # return response

    # return redirect('http://www.qq.com')

@app.route('/user/<id>')
def get_user(id):
    user = load_user(id)
    if not user:
        abort(404)
    return '<h1>Hello, %s</h1>' % user.name

# @app.route('/user/<name>')
# def user(name):
#     return '<h1>Hello, {}!</h1>'.format(name)

if __name__ == '__main__':
    manager.run()