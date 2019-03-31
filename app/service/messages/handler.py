# -*- coding: utf-8 -*-

"""
消息处理器
"""
import re


class Handler(object):
    def __init__(self, callback, weight=50, **kwargs):
        self.weight = weight
        self.callback = callback


class NoticeHandler(Handler):
    """Notice 处理器，处理系统消息，如加好友、加群等消息
    TODO 待实现
    """

    def __init__(self, callback, weight=100, **kwargs):
        Handler.__init__(self, callback, weight, **kwargs)
        pass

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
            kwargs = self.collect_optional_args(check_result)
            return True, self.callback(**kwargs)

    def collect_optional_args(self, check_result):
        """
        收集可选参数，用于传递给 callback。
        通过 __init__ 的一些 flag 参数，来确定是否将某些参数传递给 callback。
        这个函数其实起到了参数过滤的作用。
        :param check_result:
        :return:
        """
        return check_result  # 暂时没啥参数需要过滤


class MessageHandler(Handler):
    """消息处理器，处理各种聊天消息（去除首尾空格换行）
    """

    def __init__(self, callback, weight=100, **kwargs):
        Handler.__init__(self, callback, weight, **kwargs)

    def check_update(self, data: dict):
        """检测 data 是否 match 当前的处理器
        在子类中实现

        Return：不匹配就返回 False，否则返回提供给 callback 的关键字参数。
        """
        pass


class CommandHandler(MessageHandler):
    """命令处理器，只处理符合命令格式的消息（去除尾部空格换行）
    """

    def __init__(self, command, callback, prefix='/', weight=250, **kwargs):
        MessageHandler.__init__(self,
                                callback,
                                weight, **kwargs)
        self.command = command
        self.prefix = prefix

    def check_update(self, data: dict):
        """检测 data 是否 match 当前的处理器
        在子类中实现

        Return：不匹配就返回 False，否则返回提供给 callback 的关键字参数。
        """
        pass


class RegexHandler(MessageHandler):
    """正则消息处理器，只处理能和 Pattern 匹配的消息

    从 message 开头开始匹配，要求完全匹配！fullmatch（去除尾部空格换行）
    """

    def __init__(self, pattern, callback, weight=300, **kwargs):
        MessageHandler.__init__(self,
                                callback,
                                weight, **kwargs)

        self.pattern = re.compile(pattern)

    def check_update(self, data: dict):
        """检测 data 是否 match 当前的处理器
        在子类中实现

        Return：不匹配就返回 False，否则返回提供给 callback 的关键字参数。
        """
        text = data['message']['text']
        match = self.pattern.fullmatch(text)
        if match:
            return {
                "match": match
            }
        else:
            return False


class KeywordHandler(MessageHandler):
    """正则消息处理器，只处理能和 Pattern 匹配的消息

    只要求匹配 message 的某一部分（去除尾部空格换行）
    """

    def __init__(self, pattern, callback, weight=300, **kwargs):
        MessageHandler.__init__(self,
                                callback,
                                weight, **kwargs)

        self.pattern = re.compile(pattern)

    def check_update(self, data: dict):
        """检测 data 是否 match 当前的处理器
        在子类中实现

        Return：不匹配就返回 False，否则返回提供给 callback 的关键字参数。
        """
        text = data['message']['text']
        match = self.pattern.search(text)
        if match:
            return {
                "match": match
            }
        else:
            return False




