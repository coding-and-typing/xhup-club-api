# -*- coding: utf-8 -*-
import logging
from pathlib import Path

"""
基础配置
"""


class BaseConfig(object):
    SECRET_KEY = '*this-really_needs-to-be-changed*'

    DEBUG = False
    TESTING = False

    # 项目根目录
    PROJECT_ROOT = Path(__file__).parent.parent.absolute()

    REDIS_URL = ""

    ELASTICSEARCH_URL = ""

    # SQLITE
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(PROJECT_ROOT / "app-dev.db")
    # 是否在每次更新数据库时给出提示（追踪修改）
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 是否开启权限鉴定
    IS_AUTH_ENABLED = False

    # 发生 error 时邮件通知 ADMINS
    IS_ERROR_MAIL_ENABLED = False

    LOG_LEVEL = logging.DEBUG

    ADMINS = ['xiaoyin_c@qq.com']


