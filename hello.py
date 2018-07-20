from flask import Flask, render_template, request
from flask_script import Manager, Server
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required

from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hardtoguess12345HARD'
manager = Manager(app)
manager.add_command("runserver", Server(use_debugger=True))
Bootstrap = Bootstrap(app)
moment = Moment(app)

my_dict = {'key': 'test'}

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


# before '/'
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/')
def index():
    form = NameForm(request.form)
    return render_template('index.html', current_time=datetime.utcnow(), form=form)


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name, user='user')

if __name__ == '__main__':
    manager.run()
