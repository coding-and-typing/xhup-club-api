# -*- coding: utf-8 -*-
from flask import Blueprint, Flask
from flask_sockets import Sockets

# websocket 路径前缀
ws_prefix = "/ws"

from .bot import *
from .web import *

"""
WebSocket 事件处理

---
使用了 flask-sockets，这个插件是对 gevent-websocket 的一个超简单的封装，总代码仅 113 行。

Note: WebSocket 的 url 并没有被直接注册到 app，因此 app.url_map 中是看不到 ws api 的
    url 是在 sockets 实例的 url_map 属性中。
"""


def init_websockets(sockets: Sockets):
    # 将 flask_sockets 的 blueprint 注册到 sockets 实例
    sockets.register_blueprint(bot_bp)
    sockets.register_blueprint(web_bp)

