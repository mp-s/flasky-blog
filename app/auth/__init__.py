from flask import Blueprint

auth = Blueprint('auth', __name__)

# 在末尾导入, 防止循环导入依赖
from . import views