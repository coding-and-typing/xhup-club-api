# -*- coding: utf-8 -*-

"""
实用函数
"""
import time

import chardet
import random
import re
from flask_login import login_required as login_required_
from flask_rest_api.utils import deepupdate


def login_required(func):
    """包装 flask-login 的 login_required 装饰器
    给该函数的 401 响应添加 api doc
    """

    doc = {'responses': {"401": {'description': "需要先登录，才能调用此 api"}}}
    func._api_manual_doc = deepupdate(getattr(func, '_api_manual_doc', {}), doc)

    return login_required_(func)


def timestamp():
    """Return the current timestamp as an integer."""
    return int(time.time())


def auto_decode(content: bytes):
    """检测编码，读取文件"""
    encoding = chardet.detect(content)['encoding']  # 检测编码

    return content.decode(encoding)


def shuffle_text(text: str):
    """文本乱序，添加单字赛文时可能需要"""
    text_list = [*text]
    random.shuffle(text_list)

    return "".join(text_list)

