# -*- coding: utf-8 -*-
import copy
import logging

from operator import attrgetter
from typing import Dict

from app.service.messages.handler import Handler

logger = logging.getLogger(__name__)


class Dispatcher(object):
    """
    消息分派器，暂时忽略 Notice

    platform: 平台，目前只有 qq，未来可能会添加 telegtram、wechat
    group_id: 群组id，四种可能：private（仅私聊）、group（仅群聊），或者特定的群号
    """

    def __init__(self):
        self.handlers: Dict[str, Dict[str, list]] = {
            "qq": dict(),
            "telegram": dict(),
            "wechat": dict(),
            "default": {
                "group": [],
                "private": [],
            },
        }
        self.sort_key = attrgetter("weight")  # 用于 handles 排序的 key

    def get_handlers(self, data: dict):
        """根据消息的内容，返回对应的 handlers 列表"""
        platform = data['platform']
        message = data['message']

        if message['type'] == 'group':
            group_id = message['group']['id']
            handlers = self.handlers[platform].get(group_id)  # 首先考虑使用群自定义的 handlers
            if not handlers:
                handlers = self.handlers["default"]['group']  # 没有则使用默认 handlers（这个所有平台通用）
        elif message['type'] == 'private':
            handlers = self.handlers['default']['private']  # 同样是所有平台通用
        else:
            logger.error("无法解析！消息格式不正确！")
            return None

        return handlers

    def handle_update(self, data: dict):
        """处理消息"""
        handlers = self.get_handlers(data)
        data_back = copy.deepcopy(data)  # 用于回复的 dict，在 data 上稍做修改就行
        reply = data_back['message']

        # 处理消息
        for handler in handlers:
            match, res = handler.handle_update(data)
            if match:
                if reply['type'] == "group":
                    reply['group'] = {
                        'id': reply['group']['id'],
                        'at_member': res.get("at_member")
                    }
                reply['text'] = res.get('text')
                reply['images'] = res.get('images')

        if reply['text'] or reply['image']:  # 有回复消息
            return data_back  # 这个 dict 会被发送回 qq/telegram 前端
        else:
            return None  # 没有消息要回复

    def add_handler(self, handler, platform='default', group_id="group", extra_doc=None):
        """
        注册消息处理器，default 表示该处理器为所有平台/群组所通用。

        1. 对每条消息而言，只可能触发最多一个消息处理器。处理器之间按权重排序。
        :param handler: 需要添加的 handler
        :param platform: 有 qq telegram wechat, 和 default
        :param group_id: group、private、或者群 id
        :param extra_doc: 补充的 docstring，不同的命令，在不同环境下，效果也可能不同
        :return:
        """
        if not isinstance(handler, Handler):
            raise TypeError('handlers is not an instance of {0}'.format(Handler.__name__))
        if not isinstance(platform, str):
            raise TypeError('platform is not str')
        if not isinstance(group_id, str):
            raise TypeError('group_id is not str')

        if extra_doc:  # 添加补充的说明文档
            handler.extra_doc = extra_doc

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

    def remove_handler(self, handler, platform='default', group_id="group"):
        """移除消息处理器"""
        if platform in self.handlers \
                and group_id in self.handlers[platform]:
            self.handlers[platform][group_id].remove(handler)
