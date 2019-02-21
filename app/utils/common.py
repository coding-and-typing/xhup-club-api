# -*- coding: utf-8 -*-

"""
实用函数
"""
import time
from flask_login import login_required as login_required_
from flask_rest_api.utils import deepupdate


def timestamp():
    """Return the current timestamp as an integer."""
    return int(time.time())


def login_required(func):
    """包装 flask-login 的 login_required 装饰器
    给该函数的 401 响应添加 api doc
    """

    doc = {'responses': {"401": {'description': "需要先登录，才能调用此 api"}}}
    func._api_manual_doc = deepupdate(getattr(func, '_api_manual_doc', {}), doc)

    return login_required_(func)


def send_email(destination, content):
    """
    使用配置好的邮件服务器发送邮件，用于发送账号验证邮件、重置账号密码等
    :param destination:
    :param content:
    :return:
    """

    # TODO 待实现
    pass

