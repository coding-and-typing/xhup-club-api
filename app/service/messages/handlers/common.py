# -*- coding: utf-8 -*-
import logging

import re

from app import utils
from app.service.messages import dispatcher, as_command_handler, as_regex_handler, as_at_me_handler

logger = logging.getLogger(__name__)


@as_command_handler(command="帮助",
                    weight=300,
                    prefix=("?", "？"),
                    arg_primary={
                        "name": "功能",
                        "type": str,
                        "help": "查看指定功能的帮助信息"
                    })
def usage_handler(data, session, args):
    """查看帮助信息
    可以通过"帮助 [功能]" 来查看指定功能的帮助信息
    ------
    :param data:
    :param session:
    :param args:
    :return:
    """
    reply = dict()

    handlers = dispatcher.get_handlers(data)
    fname = args['primary']  # function name
    if not fname:  # 返回所有功能的 usage
        usages = (f"{i}. {handler.synopsis}" for i, handler in enumerate(handlers))
        reply['text'] = "\n".join(usages)

    # 通过 fname 查找对应的 function
    for handler in handlers:
        if handler.name == fname:
            reply['text'] = handler.usage

    return reply


def talk_handler(data, session, message):
    """和机器人聊天
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
        reply['at_member'] = [message['user']['id'], ]
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

