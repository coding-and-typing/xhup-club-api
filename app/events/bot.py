
"""
这部分 api，专门提供给聊天机器人前端调用。

因此它不应该去依赖 flask-login ——这个是给单用户用的。

websocket 只在建立连接时需要使用到 token，token 存在数据库里边儿，不应该让其他任何人知道。

在 on_connect 时检查 token，token 就放在 url 的 query params 里边。
因此程序应该使用 ssl！！！否则会很不安全。

---
赛文续传仍然需要 session，session 用 group_user_id 标识，存在 redis 里边，设个 expire 时间。
（可这样 session 过期不会提示，还是说用 apscheduler 定时删除 session，同时向群里发送过期时间？）
"""
from flask import Blueprint

from . import ws_prefix

bot_bp = Blueprint(r'bot', __name__, url_prefix=f'{ws_prefix}/bot')


@bot_bp.route('/')
def echo_socket(socket):
    """
    TODO 待实现
    """
    while not socket.closed:
        message = socket.receive()
        socket.send(message)


