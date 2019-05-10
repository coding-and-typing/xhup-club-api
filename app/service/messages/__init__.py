# -*- coding: utf-8 -*-
from app.service.messages.dispatcher import Dispatcher
from app.service.messages.handler import MessageHandler, CommandHandler, RegexHandler, KeywordHandler

"""
处理 QQ/tg/wechat 消息。

目前仅考虑图片和纯文本，以及 at_me，其他消息一概忽略。
"""

dispatcher = Dispatcher()


def as_message_handler(weight: int):
    """将被装饰函数包装成 message handler"""
    def wrapper(f):
        return MessageHandler(f, weight)
    return wrapper


def as_command_handler(command, weight: int, prefix, args=("/",),):
    """将被装饰函数包装成 command handler"""
    def wrapper(f):
        return CommandHandler(command, f, weight, prefix, args)
    return wrapper


def as_regex_handler(pattern, weight: int, pass_groups=False, pass_groupdict=False):
    """将被装饰函数包装成 regex handler"""
    def wrapper(f):
        return RegexHandler(pattern, f, weight, pass_groups, pass_groupdict)
    return wrapper


def as_keyword_handler(pattern, weight: int):
    """将被装饰函数包装成 keyword handler"""
    def wrapper(f):
        return KeywordHandler(pattern, f, weight)
    return wrapper


from . import handlers  # 防止循环导入
