from flask import Blueprint

# 创建主蓝本
main = Blueprint('main', __name__)

# 在末尾导入, 防止循环导入依赖
from . import views, errors
from ..models import Permission


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)