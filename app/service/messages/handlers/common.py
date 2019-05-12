# -*- coding: utf-8 -*-
import logging
from typing import List

import re

from app import utils
from app.service.messages import dispatcher, as_command_handler, as_regex_handler, as_at_me_handler
from app.service.messages.handler import Handler

logger = logging.getLogger(__name__)


@as_command_handler(command="帮助",
                    weight=300,
                    prefix=("?", "？"),
                    arg_primary={
                        "name": "功能",
                        "type": str,
                        "required": False,
                        "help": "显示某功能的说明"
                    })
def usage_handler(data, session, args):
    """查看帮助信息
    “？帮助” ：显示所有支持的功能
    ------
    :param data:
    :param session:
    :param args:
    :return:
    """
    reply = dict()

    handlers: List[Handler] = dispatcher.get_handlers(data)
    fname = args['primary']  # function name
    if not fname:  # 返回所有功能的 usage
        handler_names = set()
        handlers_uniq = []
        for h in handlers:
            # 同一个 handler 可能会注册了多个命令（比如 talk），这里做去重工作
            if h.name not in handler_names:
                handler_names.add(h.name)
                handlers_uniq.append(h)

        usages = (f"{i}. {h.synopsis}" for i, h in enumerate(handlers_uniq))
        reply['text'] = "\n".join(usages)

    # 通过 fname 查找对应的 function
    for handler in handlers:
        if handler.name == fname:
            reply['text'] = handler.usage

    return reply


def talk_handler(data, session, message):
    """和机器人聊天
    1. 在群内 @ 我
    2. 信息以“：”开头，例如“：你好”
    ---
    :param data:
    :param session:
    :param message:
    :return:
    """
    group_id = message['group']['id'] if message['type'] == "group" else None

    reply = dict()
    text = re.sub(r"^(?:\:|：)", '', message['text'])  # 对
    reply['text'] = utils.web.talk(text,
                                   message['user']['id'],
                                   group_id)

    if group_id:
        reply['at_members'] = [message['user']['id'], ]
    return reply


at_me_talk_handler = as_at_me_handler(weight=300, name="聊天", pass_message=True)(talk_handler)
regex_talk_handler = as_regex_handler(
    re.compile(r"(?:\:|：)\S+.*"),
    weight=300, name="聊天", pass_message=True)(talk_handler)

# 添加默认 handlers
# 1. 帮助命令
dispatcher.add_handler(usage_handler, platform="default", group_id="group")
dispatcher.add_handler(usage_handler, platform="default", group_id="private")

# 2. 聊天机器人
dispatcher.add_handler(at_me_talk_handler, platform="default", group_id="group")  # 只有群内才能 at

dispatcher.add_handler(regex_talk_handler, platform="default", group_id="group")
dispatcher.add_handler(regex_talk_handler, platform="default", group_id="private")

