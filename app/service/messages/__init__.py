

"""
处理 QQ/tg/wechat 消息。

目前仅考虑图片和纯文本，以及 at_me，其他消息一概忽略。
"""
from app.service.messages.dispatcher import Dispatcher

dispatcher = Dispatcher()


from . import handlers  # 防止循环导入
