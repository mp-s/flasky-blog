from flask import Flask, render_template
from flask_script import Manager, Server
from flask_bootstrap import Bootstrap


app = Flask(__name__)
manager = Manager(app)
manager.add_command("runserver", Server(use_debugger=True))
Bootstrap = Bootstrap(app)

my_dict = {'key': 'test'}

@app.route('/')
def index():
    return render_template('index.html', mydict=my_dict)


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name, user='user')

if __name__ == '__main__':
    manager.run()