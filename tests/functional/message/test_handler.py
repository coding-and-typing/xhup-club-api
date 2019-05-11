# -*- coding: utf-8 -*-
from pprint import pprint

import pytest

from app.service.messages import dispatcher


def test_usage_handler(app):
    """测试帮助命令"""
    data = {
            "platform": "qq",
            "message": {  # 如果 update 类型是 message
                "type": "group",  # 'private' or 'group'
                "user": {
                    "id": "123456",  # 用户 id，QQ 号等
                    "role": "member",  # 群组 owner/admin/other
                },
                "group": {
                    "id": "234567",  # 群 id
                    "at_me": False,  # 是否是 at 我
                },

                "text": "？帮助 聊天",  # 消息的 text 部分。（去除掉了表情、at 和多媒体数据）
            },
        }
    reply = dispatcher.handle_update(data)
    assert reply == {
        'platform': 'qq',
        'message': {
            'type': 'group',
            'user': {
                'id': '123456',
                'role': 'member'
            },
            'group': {
                'id': '234567',
                'at_member': None
            },
            'text': '聊天：和机器人聊天',
            'images': None}}


def test_usage_handler(app):
    """测试帮助命令"""
    data = {
            "platform": "qq",
            "message": {  # 如果 update 类型是 message
                "type": "group",  # 'private' or 'group'
                "user": {
                    "id": "123456",  # 用户 id，QQ 号等
                    "role": "member",  # 群组 owner/admin/other
                },
                "group": {
                    "id": "234567",  # 群 id
                    "at_me": False,  # 是否是 at 我
                },

                "text": "？帮助 聊天",  # 消息的 text 部分。（去除掉了表情、at 和多媒体数据）
            },
        }
    reply = dispatcher.handle_update(data)
    assert reply == {
        'platform': 'qq',
        'message': {
            'type': 'group',
            'user': {
                'id': '123456',
                'role': 'member'
            },
            'group': {
                'id': '234567',
                'at_member': None
            },
            'text': '聊天：和机器人聊天',
            'images': None}}


def test_talk_handler(app):
    """测试帮助命令"""
    data = {
            "platform": "qq",
            "message": {  # 如果 update 类型是 message
                "type": "group",  # 'private' or 'group'
                "user": {
                    "id": "123456",  # 用户 id，QQ 号等
                    "role": "member",  # 群组 owner/admin/other
                },
                "group": {
                    "id": "234567",  # 群 id
                    "at_me": True,  # 是否是 at 我
                },

                "text": "可在呢？",  # 消息的 text 部分。（去除掉了表情、at 和多媒体数据）
            },
        }

    # 1. 处理 at_me 的情况
    reply = dispatcher.handle_update(data)
    assert reply
    assert reply['message']['text'] not in ["暂不提供该功能", "异常状况，即将崩坏。9 8 7..."]

    # 2. 处理使用 regex 的情况
    data['message']['group']['at_me'] = False
    data['message']['text'] = '：' + data['message']['text']
    reply = dispatcher.handle_update(data)
    assert reply
    assert reply['message']['text'] not in ["暂不提供该功能", "异常状况，即将崩坏。9 8 7..."]



