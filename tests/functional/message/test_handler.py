# -*- coding: utf-8 -*-
from pprint import pprint

import pytest
from flask import url_for
from flask.testing import FlaskClient

from app.service.messages import dispatcher
from app.service.words import character
from app.utils.db import get_group
from tests.api.test_character import test_post_table_query
from tests.conftest import group_id, platform, login


def test_usage_handler(app):
    """1. 测试帮助命令"""
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

                "text": "？帮助 查字",  # 消息的 text 部分。（去除掉了表情、at 和多媒体数据）
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
                'at_members': None
            },
            'text': '查字：查询小鹤双拼拆字表\n用法：“？字”',
            'images': None}}


# 图灵机器人 API 现在一天仅有一百次调用了，不如去掉。。
# def test_talk_handler(app):
#     """2. 测试聊天命令"""
#     data = {
#             "platform": "qq",
#             "message": {  # 如果 update 类型是 message
#                 "type": "group",  # 'private' or 'group'
#                 "user": {
#                     "id": "123456",  # 用户 id，QQ 号等
#                     "role": "member",  # 群组 owner/admin/other
#                 },
#                 "group": {
#                     "id": "234567",  # 群 id
#                     "at_me": True,  # 是否是 at 我
#                 },
#
#                 "text": "啥情况？",  # 消息的 text 部分。（去除掉了表情、at 和多媒体数据）
#             },
#         }
#
#     # 1. 处理 at_me 的情况
#     reply = dispatcher.handle_update(data)
#     assert reply
#     assert reply['message']['text'] not in ["暂不提供该功能", "异常状况，即将崩坏。9 8 7..."]
#
#     # 2. 处理使用 regex 的情况
#     data['message']['group']['at_me'] = False
#     data['message']['text'] = '：' + data['message']['text']
#     reply = dispatcher.handle_update(data)
#     assert reply
#     assert reply['message']['text'] not in ["暂不提供该功能", "异常状况，即将崩坏。9 8 7..."]


def test_char_query_handler(user, client: FlaskClient, group_admin):
    """3. 测试小鹤拆字命令"""
    # 1. 首先上传拆字表
    payload = {
        "version": "0.0.1",
        "table_name": "小鹤音形拆字表",
        "table_type": "xhup",
        "description": "最初的版本，小鹤音形是双拼+形的四键编码方案。",
        "table": """比：　bi bibb*=拆分：　比左 匕=首末：　比左 匕=编码：　b  b
    顷：　qkb qkbr=拆分：　比左 一 ノ 冂 人=首末：　比左 人=编码：　b  r
    皆：　jpb jpbb=拆分：　比左 匕 白=首末：　比左 白=编码：　b  b""",
        "group_id": group_id,
        "platform": platform,
    }
    login(client)
    character.save_char_table(**payload, main_user=user)

    # 2. 测试查字
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

                "text": "？皆",  # 消息的 text 部分。（去除掉了表情、at 和多媒体数据）
            },
        }

    # 1. 处理 at_me 的情况
    reply = dispatcher.handle_update(data)
    assert reply
    assert reply['message']['text'] == "皆：　jpb jpbb\n" \
                                       "拆分：　比左 匕 白\n" \
                                       "首末：　比左 白\n" \
                                       "编码：　b b\n" \
                                       "汉典：http://xhup.club/?UQ"


def test_group_binding(user, group_admin, client: FlaskClient):
    login(client)

    resp = client.post(url_for("relation.RelationView"))  # 获取验证码

    data = {
            "platform": "qq",
            "message": {  # 如果 update 类型是 message
                "type": "group",  # 'private' or 'group'
                "user": {
                    "id": "123456",  # 用户 id，QQ 号等
                    "nickname": "riki",
                    "role": "owner",  # 群组 owner/admin/other
                },
                "group": {
                    "id": "234567",  # 群 id
                    "name": "234567",
                    "at_me": False,  # 是否是 at 我
                },

                "text": f"？群组绑定 {resp.json['verification_code']}",  # 消息的 text 部分。（去除掉了表情、at 和多媒体数据）
            },
        }
    reply = dispatcher.handle_update(data)
    assert reply['message']['text'] == "绑定完成！"
    group = get_group(platform="qq", group_id="234567")
    assert group is not None
    assert group in user.auth_groups

