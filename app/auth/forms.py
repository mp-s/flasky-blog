from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


# 登入
class LoginForm(FlaskForm):
    ''' 登入 '''
    email = StringField('Email',
                        validators=[DataRequired(),
                                    Length(1, 64),
                                    Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


# 注册
class RegisterationForm(FlaskForm):
    ''' 注册 '''
    email = StringField('Email',
                        validators=[DataRequired(),
                                    Length(1, 64),
                                    Email()])
    username = StringField('Username',
                           validators=[
                               DataRequired(),
                               Length(1, 64),
                               Regexp(
                                   '^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                   'Usernames must have only letters, '
                                   'numbers, dots or underscores')
                           ])
    password = PasswordField('Password',
                             validators=[
                                 DataRequired(),
                                 EqualTo('password2',
                                         message='Password must match.')
                             ])
    password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


# 改密码
class ChangePasswordForm(FlaskForm):
    ''' 改密码 '''
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    password = PasswordField('New Password',
                             validators=[
                                 DataRequired(),
                                 EqualTo('password2',
                                         message='Passwords must match.')
                             ])
    password2 = PasswordField('Confirm New Password',
                              validators=[DataRequired()])
    submit = SubmitField('Update Password')


# 重置密码前确认邮箱
class PasswordResetRequestForm(FlaskForm):
    ''' 重置密码前确认邮箱 '''
    email = StringField('Email',
                        validators=[DataRequired(),
                                    Length(1, 64),
                                    Email()])
    submit = SubmitField('Reset Password')


# 重置密码
class PasswordResetForm(FlaskForm):
    ''' 重置密码 '''
    password = PasswordField('New Password',
                             validators=[
                                 DataRequired(),
                                 EqualTo('password2',
                                         message='Passwords must match.')
                             ])
    password2 = PasswordField('Confirm new password',
                              validators=[DataRequired()])
    submit = SubmitField('Reset Password')


# 更改邮箱
class ChangeEmailForm(FlaskForm):
    ''' 更改邮箱 '''
    email = StringField('New Email',
                        validators=[DataRequired(),
                                    Length(1, 64),
                                    Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
