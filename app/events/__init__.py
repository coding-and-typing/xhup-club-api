# -*- coding: utf-8 -*-
from flask import Blueprint, Flask

"""
WebSocket 事件处理
"""

ws_bp = Blueprint('ws', __name__, url_prefix='/ws')


def init_app(app: Flask):
    app.register_blueprint(ws_bp)
