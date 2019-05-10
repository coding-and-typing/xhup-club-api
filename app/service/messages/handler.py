# -*- coding: utf-8 -*-

"""
消息处理器
"""
import re

from app.service.messages.argparse import ArgumentParser
from app.service.messages.session import Session


class Handler(object):
    def __init__(self, callback, weight, extra_doc=""):
        self.weight = weight
        self.callback = callback
        self.usage = callback.__doc__
        self.extra_doc = extra_doc

    def check_update(self, data: dict):
        """检测 data 是否 match 当前的处理器
        在子类中实现

        Return：不匹配就返回 False，否则返回提供给 callback 的关键字参数。
        """
        raise NotImplementedError

    def handle_update(self, data):
        """处理数据"""

        check_result = self.check_update(data)
        if not check_result:
            return False, None
        else:
            optional_kwargs = self.collect_optional_args(check_result)
            return True, self.callback(data, Session(data), **optional_kwargs)

    def collect_optional_args(self, check_result):
        """
        收集可选参数，用于传递给 callback。
        通过 __init__ 的一些 flag 参数，来确定是否将某些参数传递给 callback。
        这个函数其实起到了参数过滤的作用。
        :param check_result:
        :return:
        """
        return dict()  # 暂时没啥参数需要过滤


class NoticeHandler(Handler):
    """Notice 处理器，处理系统消息，如加好友、加群等消息
    """

    def check_update(self, data: dict):
        """TODO 待实现

        :param data:
        :return:
        """

    def __init__(self, callback, weight, extra_doc=""):
        Handler.__init__(self, callback, weight, extra_doc)
        pass


class MessageHandler(Handler):
    """消息处理器，处理各种聊天消息（去除首尾空格换行）
    """

    def __init__(self, callback, weight, extra_doc=""):
        Handler.__init__(self, callback, weight, extra_doc)

    def check_update(self, data: dict):
        """检测 data 是否 match 当前的处理器
        """
        return True  # 任何消息都会触发 callback 函数


class CommandHandler(MessageHandler):
    """命令处理器，只处理符合命令格式的消息（去除尾部空格换行）
    """

    def __init__(self,
                 command,
                 callback,
                 weight,
                 prefix: tuple,
                 args=tuple(),
                 pass_args=True,
                 extra_doc=""):
        MessageHandler.__init__(self, callback, weight, extra_doc)
        self.command = command
        self.prefix = prefix
        self.pass_args = pass_args

        self.args_parser = ArgumentParser.make_args_parser(command, callback.__doc__, args)
        self.usage = self.args_parser.usage

    def check_update(self, data: dict):
        """检测 data 是否 match 当前的处理器

        Return：不匹配就返回 False，否则返回待处理的 dict
        """
        command = data['message']['text']

        # 1. 前缀是否匹配
        if command[0] in self.prefix:
            command = command[1:]
        else:
            return False

        # 2. 解析额外的参数
        args = self.args_parser.parse(command)

        if args:
            return {"args": args}
        else:
            return False

    def collect_optional_args(self, check_result):
        optional_kwargs = super(CommandHandler, self).collect_optional_args(check_result)
        if self.pass_args:
            optional_kwargs['args'] = check_result['args']
        return optional_kwargs


class RegexHandler(MessageHandler):
    """正则消息处理器，只处理能和 Pattern 匹配的消息

    从 message 开头开始匹配，要求完全匹配！fullmatch（去除尾部空格换行）
    """

    def __init__(self,
                 pattern,
                 callback,
                 weight,
                 extra_doc="",
                 pass_groups=False,
                 pass_groupdict=False):
        MessageHandler.__init__(self, callback, weight, extra_doc)

        self.pattern = re.compile(pattern)
        self.pass_groups = pass_groups
        self.pass_groupdict = pass_groupdict

    def check_update(self, data: dict):
        """检测 data 是否 match 当前的处理器
        在子类中实现

        Return：不匹配就返回 False，否则返回提供给 callback 的关键字参数。
        """
        text = data['message']['text']
        match = self.pattern.fullmatch(text)
        if match:
            return {"match": match}
        else:
            return False

    def collect_optional_args(self, check_result):
        optional_kwargs = super(RegexHandler, self).collect_optional_args(check_result)
        if self.pass_groups:
            optional_kwargs['groups'] = check_result['match'].groups()
        if self.pass_groupdict:
            optional_kwargs['groupdict'] = check_result['match'].groupdict()
        return optional_kwargs


class KeywordHandler(MessageHandler):
    """关键字处理器，只处理包含 Pattern 的消息

    只要求匹配 message 的某一部分（去除尾部空格换行）
    """

    def __init__(self,
                 pattern,
                 callback,
                 weight,
                 extra_doc=""):
        MessageHandler.__init__(self, callback, weight, extra_doc)

        self.pattern = re.compile(pattern)

    def check_update(self, data: dict):
        """检测 data 是否 match 当前的处理器
        """
        text = data['message']['text']
        match = self.pattern.search(text)

        return True if match else False
