from flask import Blueprint

api = Blueprint('api', __name__)

# 在末尾导入, 防止循环导入依赖
from . import authentication, posts, users, comments, errors
