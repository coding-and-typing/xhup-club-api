# -*- coding: utf-8 -*-
from dotenv import load_dotenv
from pathlib import Path

from .base import *
from .dev import *
from .test import *
from .prod import *

"""
配置文件
"""

config_by_name = {
    "dev": DevelopmentConfig,
    "test": TestingConfig,
    "prod": ProductionConfig
}