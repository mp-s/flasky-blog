from flask import jsonify, request, current_app, url_for

from . import api
from ..models import User, Post


# 查询用户
@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


# 用户帖子
@api.route('/users/<int:id>/posts/')
def get_user_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pgination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page,
        per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pgination.items
    prev = None
    if pgination.has_prev:
        prev = url_for('api.get_user_posts', id=id, page=page - 1)
    _next = None
    if pgination.has_next:
        _next = url_for('api.get_user_posts', id=id, page=page + 1)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': _next,
        'count': pgination.total
    })


# 用户时间线
@api.route('/users/<int:id>/timeline/')
def get_user_followed_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page,
        per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items

    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_followed_posts', id=id, page=page - 1)

    _next = None
    if pagination.has_next:
        _next = url_for('api.get_user_followed_posts', id=id, page=page + 1)

    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': _next,
        'count': pagination.total
    })
