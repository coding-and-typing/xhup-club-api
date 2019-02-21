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
    """socketio 版本的 login_required"""

    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

