# -*- coding: utf-8 -*-
import logging

import re

from app.service.messages import dispatcher, as_command_handler, as_regex_handler


logger = logging.getLogger(__name__)


@as_command_handler(command="帮助",
                    weight=300,
                    prefix=("?", "？"),
                    arg_primary={
                        "name": "功能",
                        "type": str,
                        "help": "查看指定功能的帮助信息"
                    })
def usage(data, session, args):
    handlers = dispatcher.get_handlers(data)
    fname = args['primary']  # function name
    if not fname:  # 返回所有功能的 usage
        usages = (f"{i}. {handler.synopsis}" for i, handler in enumerate(handlers))
        return "\n".join(usages)

    # 通过 fname 查找对应的 function
    for handler in handlers:
        if handler.name == fname:
            return handler.usage

