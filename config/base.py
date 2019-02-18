# -*- coding: utf-8 -*-
from pathlib import Path

"""
基础配置
"""


class BaseConfig(object):
    SECRET_KEY = '*this-really_needs-to-be-changed*'

    # 项目根目录
    PROJECT_ROOT = Path(__file__).parent.parent.absolute()

    # SQLITE
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(PROJECT_ROOT / "app-test.db")
    # 跟踪对象的修改
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    DEBUG = False
    ERROR_404_HELP = False


