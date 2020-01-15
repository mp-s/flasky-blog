from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField
from wtforms import (StringField, SubmitField, TextAreaField, BooleanField,
                     SelectField, ValidationError)
from wtforms.validators import DataRequired, Length, Email, Regexp
from ..models import Role, User


# 用户名字
class NameForm(FlaskForm):
    ''' 用户名字 '''
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


# 资料编辑
class EditProfileForm(FlaskForm):
    ''' 资料编辑 '''
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


# 管理员级别资料编辑
class EditProfileAdminForm(FlaskForm):
    ''' 管理员级别资料编辑 '''
    email = StringField('Email',
                        validators=[DataRequired(),
                                    Length(1, 64),
                                    Email()])
    username = StringField('usename',
                           validators=[
                               DataRequired(),
                               Length(1, 64),
                               Regexp(
                                   '^[A-Za-z][A-za-z0-9_.]*$', 0,
                                   'Usernames must have only letters, '
                                   'numbers, dots or underscores')
                           ])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if (field.data != self.user.email
                and User.query.filter_by(email=field.data).first()):
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if (field.data != self.user.username
                and User.query.filter_by(username=field.data).first()):
            raise ValidationError('username already in use.')


# 发表文字
class PostForm(FlaskForm):
    ''' 发表文字 '''
    body = PageDownField("what's on your mind?", validators=[DataRequired()])
    submit = SubmitField('Submit')


# 发表评论
class CommentForm(FlaskForm):
    ''' 发表评论 '''
    body = StringField('', validators=[DataRequired()])
    submit = SubmitField('Submit')
