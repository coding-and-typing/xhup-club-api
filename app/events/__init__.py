# -*- coding: utf-8 -*-
from flask_sockets import Sockets

# websocket 路径前缀
from app import limiter

ws_prefix = "/ws"

from .bot import *

"""
WebSocket 事件处理

---
使用了 flask-sockets，这个插件是对 gevent-websocket 的一个超简单的封装，总代码仅 113 行。

Note: WebSocket 的 url 并没有被直接注册到 app，因此 app.url_map 中是看不到 ws api 的
    url 是在 sockets 实例的 url_map 属性中。
"""


def init_websockets(sockets: Sockets):
    # ip 访问频率限制（防破解）
    # TODO 这个好像没用，大概是因为这边的路由并不是由 app 处理的？
    limiter.limit("600/day;100/hour;1/minute;1/second")(bot_bp)

    # 将 flask_sockets 的 blueprint 注册到 sockets 实例
    sockets.register_blueprint(bot_bp)

