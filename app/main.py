# -*- coding: utf-8 -*-

import logging
from flask import Blueprint

logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)


@main.before_app_request
def before_request():
    """安全检查：api_key sign 与 timestamp 验证"""
    # TODO api 权限检测（该客户端是拥有授权）
    # 参考 https://www.cnblogs.com/marszhw/p/6030972.html
    pass


# 错误处理


# TODO 展示 swagger UI 的 RESTFul Docs

