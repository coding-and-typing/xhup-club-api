

"""
处理 QQ/tg/wechat 消息。

目前仅考虑图片和纯文本，其他消息一概忽略。
"""

update_format = {
    "platform": 'qq',  # or 'telegram'、'wechat'
    "type": "message",  # or 'notice'
    "message": {  # 如果 update 类型是 message
        "type": "private",  # or 'group'
        "user_id": "",  # 用户 id，QQ 号等
        "text": "",  # 消息的 text 部分。（去除掉了表情、at 和多媒体数据）
        "photo": "",  # 图片路径

        # 下列属性仅 group 可用
        "group_id": "",  # 群 id
        "at_me": True,  # 是否是 at 我
    },
    "notice": {  # 如果 update 类型是 notice 的话
        # TODO 暂时未实现
    }
}


def handle_update(data: str):
    """消息处理的入口"""
    # TODO 待实现
    return data
