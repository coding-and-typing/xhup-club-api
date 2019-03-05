# -*- coding: utf-8 -*-
import functools
from flask import Blueprint, Flask
from flask_login import current_user
from flask_socketio import disconnect

"""
WebSocket 事件处理
"""

ws_bp = Blueprint('ws', __name__, url_prefix='/api/v1/ws')


def init_app(app: Flask):
    app.register_blueprint(ws_bp)


def authenticated_only(f):
    """socketio 版本的 login_required

    这个装饰器用于 Web 页面相关的 api（即适用于单用户）
    """
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


def token_required(f):
    """需要 token

    这个装饰器用于聊天机器人相关的 api
    chatbot 是系统内部的工具，因此开放的权限比较多，token 必须要藏好别让人知道了。。

    Note：token 是直接放在 url 参数内的，因此必须使用 ssl 才安全！！！
    """
    # TODO 待实现


