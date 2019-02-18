# -*- coding: utf-8 -*-
import os

from config import BaseConfig

"""
travis-ci 等集成测试用的配置
"""


class TestingConfig(BaseConfig):
    TESTING = True

    # Use in-memory SQLite database for testing（empty url for in-memory）
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
