# -*- coding: utf-8 -*-
from app.service.messages.dispatcher import Dispatcher
from app.service.messages.handler import MessageHandler, CommandHandler, RegexHandler, KeywordHandler, AtMeHandler

"""
处理 QQ/tg/wechat 消息。

目前仅考虑图片和纯文本，以及 at_me，其他消息一概忽略。
"""

dispatcher = Dispatcher()


def as_message_handler(weight: int, name, pass_message=False):
    """将被装饰函数包装成 message handler"""
    def wrapper(f):
        return MessageHandler(f, weight, name, pass_message=pass_message)
    return wrapper


def as_at_me_handler(weight: int, name, pass_message=False):
    """将被装饰函数包装成 at me handler"""
    def wrapper(f):
        return AtMeHandler(f, weight, name, pass_message=pass_message)
    return wrapper


def as_command_handler(command, weight: int,
                       prefix=("/",),
                       name=None,
                       arg_primary=None,
                       args=tuple(),
                       pass_message=False):
    """将被装饰函数包装成 command handler"""
    def wrapper(f):
        return CommandHandler(command, f, weight, prefix,
                              name=name,
                              arg_primary=arg_primary,
                              kwargs=args,
                              pass_message=pass_message)
    return wrapper


def as_regex_handler(pattern, weight: int, name,
                     pass_message=False,
                     pass_groups=False,
                     pass_groupdict=False):
    """将被装饰函数包装成 regex handler"""
    def wrapper(f):
        return RegexHandler(pattern, f, weight, name,
                            pass_message=pass_message,
                            pass_groups=pass_groups,
                            pass_groupdict=pass_groupdict)
    return wrapper


def as_keyword_handler(pattern, weight: int, name=None, pass_message=False):
    """将被装饰函数包装成 keyword handler"""
    def wrapper(f):
        return KeywordHandler(pattern, f, weight, name,
                              pass_message=pass_message)
    return wrapper


from . import handlers  # 防止循环导入
