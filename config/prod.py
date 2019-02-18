# -*- coding: utf-8 -*-
import os

from config import BaseConfig

"""
生产环境配置
"""


class ProductionConfig(BaseConfig):
    SECRET_KEY = os.getenv('XHUP_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('XHUP_SQLALCHEMY_DATABASE_URI')
