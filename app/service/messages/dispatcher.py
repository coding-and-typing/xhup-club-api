# -*- coding: utf-8 -*-
from operator import attrgetter
from typing import Dict

from app.service.messages.handler import Handler


class Dispatcher(object):
    """
    消息分派器，暂时忽略 Notice

    platform: 平台，目前只有 qq，未来可能会添加 telegtram、wechat
    group_id: 群组id，四种可能：default（所有）、private（仅私聊）、group（仅群聊），或者特定的群号
    """

    def __init__(self):
        self.handlers: Dict[str, Dict[str, list]] = {}  # platform:group_id，内层是已排序的 handlers list.
        self.sort_key = attrgetter("weight")

    def handle_update(self, data: dict):
        """处理消息"""
        platform = data['platform']
        message = data['message']
        if message['type'] == 'group':
            for p, g_id in [(platform, message['group']['id']),  # 由特殊到一般
                            (platform, "group"),
                            (platform, "default"),
                            ("default", "default")]:
                match, reply = self._handle(data, p, g_id)
                if match:
                    return reply
        elif message['type'] == 'private':
            for p, g_id in [(platform, "private"),
                            (platform, "default"),
                            ("default", "default")]:
                match, reply = self._handle(data, p, g_id)
                if match:
                    return reply

    def _handle(self, data: dict, platform: str = "default", group_id: str = "default"):
        """
        使用 `self.handlers[platform][group_id]` 中的处理器来处理消息（如果存在的话）
        :param data: 数据
        :param platform: 平台
        :param group_id: 群组id
        :return: match 表示是否匹配上，如果匹配上了，后续的 handler 就不需要调用了。
                 reply 是回复
        """""
        if platform in self.handlers \
                or group_id in self.handlers[platform]:
            for handler in self.handlers[platform][group_id]:
                match, reply = handler.handle_update(data)
                if match:
                    return match, reply

        return False, None

    def add_handler(self, handler, platform='default', group_id="default"):
        """
        注册消息处理器，default 表示该处理器为所有平台/群组所通用。

        1. 对每条消息而言，只可能触发最多一个消息处理器。处理器之间按权重排序。
        2. 如果 group 不为 default，那么 platform 也不能为 default！
        :param handler:
        :param platform:
        :param group_id:
        :return:
        """
        if not isinstance(handler, Handler):
            raise TypeError('handlers is not an instance of {0}'.format(Handler.__name__))
        if not isinstance(platform, str):
            raise TypeError('platform is not str')
        if not isinstance(group_id, str):
            raise TypeError('group_id is not str')

        if platform not in self.handlers:
            self.handlers[platform] = {
                group_id: [handler]
            }
        elif group_id not in self.handlers[platform]:
            self.handlers[platform][group_id] = [handler]
        else:
            handlers_list = self.handlers[platform][group_id]
            handlers_list.append(handler)
            handlers_list.sort(key=self.sort_key, reverse=True)  # 权重高的优先

    def remove_handler(self, handler, platform='default', group_id="default"):
        """移除消息处理器"""
        if platform in self.handlers \
                and group_id in self.handlers[platform]:
            self.handlers[platform][group_id].remove(handler)
