# -*- coding: utf-8 -*-

import logging
from flask import Blueprint

from app import db

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)


@main_bp.before_app_request
def before_request():
    """安全检查：api_key sign 与 timestamp 验证"""
    # TODO api 权限检测（该客户端是拥有授权）
    # 参考 https://www.cnblogs.com/marszhw/p/6030972.html
    pass


# 错误处理
@main_bp.app_errorhandler(404)
def not_found_error(error):
    return {
        "status": "404 not found"
    }, 404


@main_bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return {
        "status": "internal error"
    }, 500
