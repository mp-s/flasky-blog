from flask import Blueprint

# 创建主蓝本
main = Blueprint('main', __name__)

# 在末尾导入, 防止循环导入依赖
from . import views, errors
from ..models import Permission


# Permission 类加入模板上下文
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
