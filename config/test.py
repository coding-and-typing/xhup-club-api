# -*- coding: utf-8 -*-
import os

from config import BaseConfig

"""
travis-ci 等集成测试用的配置
"""


class TestingConfig(BaseConfig):
    TESTING = True
    RATELIMIT_ENABLED = False  # 测试时，关掉 ip 访问频率限制

    # 测试使用 SQLite 内存数据库，以保证测试环境一致
