# -*- coding: utf-8 -*-

"""
提供给 web 前端的 api

绑定 QQ 用户与 QQ 群

1. 当用户请求绑定 QQ群 时，前端请求此 api
2. 然后后端收到请求将生成一个随机验证码
    1. 将该 验证码、要求验证的用户 id、时间戳放入 redis，该 redis 需要设置一个失效时间
    2. 将验证码、失效时间返回给前端
    3. 等待特殊的 redis 队列被写入消息
    4. 如果收到消息，检查收到的消息是否和验证码对应
        1. 对应，就直接返回给客户端，然后关闭连接。
        2. 不对应，那估计是以前的绑定消息。
            1. 丢弃或返回给客户端
            2. 回到第三步
3. 当 xhup-qq-bot 收到验证码时（验证消息格式：`拆小鹤验证：xxxxxx`）
    1. 会通过 websocket 将QQ用户信息与验证码发送到后端
4. 后端从 redis 中查询对应的验证数据，若存在并且时间不超过三分钟
    1. 将 QQ 信息写入数据库，绑定成功。
    1. 将返回信息和对应的验证码写入 redis，由验证用的 websocket 接收（这个信息是否需要考虑没有被消费的情况？）
"""

from flask import Blueprint

from . import ws_prefix

web_bp = Blueprint(r'web', __name__, url_prefix=f'{ws_prefix}/web')


@web_bp.route('/bind_group')
def echo_socket(socket):
    """
    TODO 待实现
    """
    while not socket.closed:
        message = socket.receive()
        socket.send(message)