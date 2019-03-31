

"""
处理 QQ/tg/wechat 消息。

目前仅考虑图片和纯文本，以及 at_me，其他消息一概忽略。
"""
from app.service.messages.dispatcher import Dispatcher

dispatcher = Dispatcher()


def on_message():
    pass


def on_command(command, prefix):
    pass


def on_regex(pattern):
    pass


def on_keyword(pattern):
    pass



from . import plugins  # 防止循环导入
